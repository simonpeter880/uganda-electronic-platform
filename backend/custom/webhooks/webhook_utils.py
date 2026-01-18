"""
Webhook utilities for mobile money integrations
Provides idempotency, security, and logging helpers
"""

import hashlib
import hmac
import logging
from typing import Optional, Dict, Any
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

logger = logging.getLogger(__name__)


class WebhookIdempotency:
    """
    Idempotency handler for webhooks

    Prevents duplicate processing of the same webhook event
    Uses Django cache to store processed event IDs
    """

    # Cache TTL for processed events (24 hours)
    CACHE_TTL = 60 * 60 * 24

    @classmethod
    def get_cache_key(cls, provider: str, event_id: str) -> str:
        """Generate cache key for webhook event"""
        return f"webhook_processed:{provider}:{event_id}"

    @classmethod
    def is_processed(cls, provider: str, event_id: str) -> bool:
        """
        Check if webhook event has been processed

        Args:
            provider: Provider name (mtn, airtel)
            event_id: Unique event identifier

        Returns:
            True if already processed, False otherwise
        """
        cache_key = cls.get_cache_key(provider, event_id)
        return cache.get(cache_key) is not None

    @classmethod
    def mark_processed(cls, provider: str, event_id: str) -> None:
        """
        Mark webhook event as processed

        Args:
            provider: Provider name
            event_id: Unique event identifier
        """
        cache_key = cls.get_cache_key(provider, event_id)
        cache.set(cache_key, True, cls.CACHE_TTL)
        logger.info(f"Webhook marked as processed: {provider}/{event_id}")


class WebhookSecurity:
    """
    Security helpers for webhook validation

    Provides signature verification and IP validation
    """

    @staticmethod
    def verify_signature(
        payload: bytes,
        signature: str,
        secret: str,
        algorithm: str = 'sha256'
    ) -> bool:
        """
        Verify HMAC signature

        Args:
            payload: Raw request body bytes
            signature: Signature from request header
            secret: Shared secret key
            algorithm: Hash algorithm (sha256, sha512, etc.)

        Returns:
            True if signature is valid, False otherwise
        """
        if not secret or not signature:
            logger.warning("Missing signature or secret for verification")
            return False

        try:
            # Get hash function
            if algorithm == 'sha256':
                hash_func = hashlib.sha256
            elif algorithm == 'sha512':
                hash_func = hashlib.sha512
            else:
                logger.error(f"Unsupported hash algorithm: {algorithm}")
                return False

            # Calculate expected signature
            expected = hmac.new(
                secret.encode('utf-8'),
                payload,
                hash_func
            ).hexdigest()

            # Compare (constant-time comparison to prevent timing attacks)
            is_valid = hmac.compare_digest(expected, signature)

            if not is_valid:
                logger.warning("Signature verification failed")

            return is_valid

        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False

    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """
        Get real client IP address (handles proxies)

        Args:
            request: Django HTTP request

        Returns:
            Client IP address
        """
        # Check forwarded headers (common in load balancers/proxies)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take first IP in list (original client)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')

        return ip

    @staticmethod
    def validate_ip_whitelist(
        request: HttpRequest,
        allowed_ips: list[str]
    ) -> bool:
        """
        Validate that request comes from allowed IP

        Args:
            request: Django HTTP request
            allowed_ips: List of allowed IP addresses/ranges

        Returns:
            True if IP is allowed, False otherwise
        """
        if not allowed_ips:
            # No whitelist configured, allow all
            return True

        client_ip = WebhookSecurity.get_client_ip(request)

        if client_ip in allowed_ips:
            return True

        logger.warning(f"Webhook from unauthorized IP: {client_ip}")
        return False


class WebhookLogger:
    """
    Comprehensive webhook logging

    Logs all webhook requests for debugging and audit trail
    """

    @staticmethod
    def log_webhook_request(
        provider: str,
        request: HttpRequest,
        response_status: int,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log webhook request details

        Args:
            provider: Provider name (mtn, airtel)
            request: Django HTTP request
            response_status: HTTP response status code
            extra_data: Additional data to log
        """
        try:
            body = request.body.decode('utf-8')
            client_ip = WebhookSecurity.get_client_ip(request)

            log_data = {
                'provider': provider,
                'method': request.method,
                'client_ip': client_ip,
                'body': body,
                'headers': dict(request.headers),
                'response_status': response_status,
            }

            if extra_data:
                log_data.update(extra_data)

            logger.info(f"Webhook received from {provider}: {log_data}")

            # Optionally save to database for audit trail
            # WebhookLogModel.objects.create(**log_data)

        except Exception as e:
            logger.error(f"Error logging webhook: {e}")

    @staticmethod
    def log_webhook_error(
        provider: str,
        error: Exception,
        request: Optional[HttpRequest] = None
    ) -> None:
        """
        Log webhook processing error

        Args:
            provider: Provider name
            error: Exception that occurred
            request: Optional HTTP request object
        """
        log_data = {
            'provider': provider,
            'error': str(error),
            'error_type': type(error).__name__,
        }

        if request:
            log_data['client_ip'] = WebhookSecurity.get_client_ip(request)
            try:
                log_data['body'] = request.body.decode('utf-8')
            except Exception:
                pass

        logger.error(f"Webhook processing error: {log_data}", exc_info=True)


def generate_event_id(provider: str, reference_id: str) -> str:
    """
    Generate unique event ID from provider and reference

    Args:
        provider: Provider name
        reference_id: Transaction/reference ID

    Returns:
        Unique event ID
    """
    return f"{provider}:{reference_id}"


def parse_mtn_status(status: str) -> str:
    """
    Parse MTN status code to internal status

    Args:
        status: MTN status code (SUCCESSFUL, FAILED, PENDING)

    Returns:
        Internal status (successful, failed, pending)
    """
    status_map = {
        'SUCCESSFUL': 'successful',
        'FAILED': 'failed',
        'PENDING': 'pending',
    }
    return status_map.get(status.upper(), 'pending')


def parse_airtel_status(status_code: str) -> str:
    """
    Parse Airtel status code to internal status

    Args:
        status_code: Airtel status code (TS, TF, TA, TIP)

    Returns:
        Internal status (successful, failed, pending)
    """
    status_map = {
        'TS': 'successful',      # Transaction Successful
        'TF': 'failed',          # Transaction Failed
        'TA': 'pending',         # Transaction Ambiguous
        'TIP': 'pending',        # Transaction In Progress
        'CANCELLED': 'failed',   # Cancelled
    }
    return status_map.get(status_code.upper(), 'pending')
