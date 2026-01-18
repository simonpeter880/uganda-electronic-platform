"""
Enhanced Webhook Handlers for Mobile Money Payment Callbacks

Features:
- Idempotency handling (prevents duplicate processing)
- Signature verification for security
- IP whitelist validation
- Comprehensive logging
- Atomic database updates
- Retry handling

URL Configuration:
    /api/webhooks/mtn-momo/ - MTN Mobile Money callbacks
    /api/webhooks/airtel-money/ - Airtel Money callbacks
"""

import json
import logging
from typing import Dict, Any

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from django.db import transaction as db_transaction

from .webhook_utils import (
    WebhookIdempotency,
    WebhookSecurity,
    WebhookLogger,
    generate_event_id,
    parse_mtn_status,
    parse_airtel_status,
)


logger = logging.getLogger(__name__)


# =============================================================================
# MTN MOBILE MONEY WEBHOOK
# =============================================================================

@csrf_exempt
@require_POST
def mtn_momo_callback(request):
    """
    Handle MTN Mobile Money payment callback

    URL: /api/webhooks/mtn-momo/
    Method: POST
    Content-Type: application/json

    Expected payload:
    {
        "externalId": "ORD-12345",
        "referenceId": "uuid-transaction-id",
        "status": "SUCCESSFUL",  # or "FAILED", "PENDING"
        "amount": "50000",
        "currency": "UGX",
        "reason": "Payment failed reason"  # if failed
    }
    """
    try:
        # Parse request body
        body_bytes = request.body
        body_text = body_bytes.decode('utf-8')
        data = json.loads(body_text)

        logger.info(f"MTN MoMo callback received: {data}")

        # Extract payment data
        external_id = data.get('externalId')  # Your order reference
        reference_id = data.get('referenceId')  # MTN transaction ID
        status = data.get('status', 'PENDING')
        amount = data.get('amount')
        currency = data.get('currency')
        reason = data.get('reason', '')

        # Validate required fields
        if not reference_id:
            logger.error("MTN callback missing referenceId")
            return JsonResponse({
                'status': 'error',
                'message': 'Missing referenceId'
            }, status=400)

        # Generate event ID for idempotency
        event_id = generate_event_id('mtn', reference_id)

        # Check idempotency
        if WebhookIdempotency.is_processed('mtn', event_id):
            logger.info(f"MTN webhook already processed: {event_id}")
            return JsonResponse({
                'status': 'success',
                'message': 'Already processed'
            })

        # Verify signature (if configured)
        signature_header = request.headers.get('X-Callback-Signature') or request.headers.get('X-Signature')
        mtn_secret = getattr(settings, 'MTN_MOMO_WEBHOOK_SECRET', '')

        if mtn_secret and signature_header:
            if not WebhookSecurity.verify_signature(body_bytes, signature_header, mtn_secret):
                logger.error("MTN signature verification failed")
                WebhookLogger.log_webhook_request('mtn', request, 401)
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid signature'
                }, status=401)

        # Validate IP whitelist (if configured)
        allowed_ips = getattr(settings, 'MTN_MOMO_ALLOWED_IPS', [])
        if allowed_ips and not WebhookSecurity.validate_ip_whitelist(request, allowed_ips):
            WebhookLogger.log_webhook_request('mtn', request, 403)
            return JsonResponse({
                'status': 'error',
                'message': 'Unauthorized IP'
            }, status=403)

        # Process payment update
        internal_status = parse_mtn_status(status)

        # Import models here to avoid circular imports
        from ..models import MobileMoneyTransaction

        # Use atomic transaction for database updates
        with db_transaction.atomic():
            try:
                # Find the transaction
                txn = MobileMoneyTransaction.objects.select_for_update().get(
                    transaction_reference=reference_id
                )

                # Update transaction status
                txn.status = internal_status
                txn.provider_response = data

                if internal_status == 'successful':
                    txn.completed_at = timezone.now()

                    # Mark order as paid
                    order = txn.order
                    order.payment_verified = True
                    order.payment_verified_at = timezone.now()
                    order.save(update_fields=['payment_verified', 'payment_verified_at'])

                    logger.info(f"MTN payment successful: {reference_id} for order {order.number}")

                    # Trigger success actions (SMS, email, etc.)
                    from ..tasks.celery_tasks import send_payment_confirmed_sms
                    send_payment_confirmed_sms.delay(txn.id)

                elif internal_status == 'failed':
                    txn.error_message = reason or 'Payment failed'
                    logger.warning(f"MTN payment failed: {reference_id} - {reason}")

                txn.save()

                # Mark as processed (idempotency)
                WebhookIdempotency.mark_processed('mtn', event_id)

                # Log successful processing
                WebhookLogger.log_webhook_request('mtn', request, 200, {
                    'transaction_id': txn.id,
                    'order_number': order.number if internal_status == 'successful' else None,
                    'status': internal_status,
                })

                return JsonResponse({
                    'status': 'success',
                    'message': 'Webhook processed',
                    'transaction_id': str(txn.id)
                })

            except MobileMoneyTransaction.DoesNotExist:
                logger.error(f"MTN transaction not found: {reference_id}")
                WebhookLogger.log_webhook_request('mtn', request, 404, {
                    'reference_id': reference_id,
                    'error': 'Transaction not found'
                })
                return JsonResponse({
                    'status': 'error',
                    'message': 'Transaction not found'
                }, status=404)

    except json.JSONDecodeError:
        logger.error("MTN webhook invalid JSON")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)

    except Exception as e:
        logger.error(f"MTN webhook error: {e}", exc_info=True)
        WebhookLogger.log_webhook_error('mtn', e, request)
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)


# =============================================================================
# AIRTEL MONEY WEBHOOK
# =============================================================================

@csrf_exempt
@require_POST
def airtel_money_callback(request):
    """
    Handle Airtel Money payment callback

    URL: /api/webhooks/airtel-money/
    Method: POST
    Content-Type: application/json

    Expected payload:
    {
        "transaction": {
            "id": "airtel-transaction-id",
            "reference": "ORD-12345"
        },
        "status": {
            "code": "TS",  # TS=Success, TF=Failed, TA=Ambiguous, TIP=In Progress
            "message": "Transaction successful"
        },
        "data": {
            "transaction": {
                "amount": "50000",
                "currency": "UGX"
            }
        }
    }
    """
    try:
        # Parse request body
        body_bytes = request.body
        body_text = body_bytes.decode('utf-8')
        data = json.loads(body_text)

        logger.info(f"Airtel Money callback received: {data}")

        # Extract payment data (adjust based on Airtel's actual format)
        transaction_data = data.get('transaction', {})
        status_data = data.get('status', {})

        transaction_id = transaction_data.get('id') or transaction_data.get('reference')
        status_code = status_data.get('code', 'TIP')
        status_message = status_data.get('message', '')

        # Validate required fields
        if not transaction_id:
            logger.error("Airtel callback missing transaction ID")
            return JsonResponse({
                'status': 'error',
                'message': 'Missing transaction ID'
            }, status=400)

        # Generate event ID for idempotency
        event_id = generate_event_id('airtel', transaction_id)

        # Check idempotency
        if WebhookIdempotency.is_processed('airtel', event_id):
            logger.info(f"Airtel webhook already processed: {event_id}")
            return JsonResponse({
                'status': 'success',
                'message': 'Already processed'
            })

        # Verify signature (if configured)
        signature_header = request.headers.get('X-Signature') or request.headers.get('Authorization')
        airtel_secret = getattr(settings, 'AIRTEL_MONEY_WEBHOOK_SECRET', '')

        if airtel_secret and signature_header:
            if not WebhookSecurity.verify_signature(body_bytes, signature_header, airtel_secret):
                logger.error("Airtel signature verification failed")
                WebhookLogger.log_webhook_request('airtel', request, 401)
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid signature'
                }, status=401)

        # Validate IP whitelist (if configured)
        allowed_ips = getattr(settings, 'AIRTEL_MONEY_ALLOWED_IPS', [])
        if allowed_ips and not WebhookSecurity.validate_ip_whitelist(request, allowed_ips):
            WebhookLogger.log_webhook_request('airtel', request, 403)
            return JsonResponse({
                'status': 'error',
                'message': 'Unauthorized IP'
            }, status=403)

        # Process payment update
        internal_status = parse_airtel_status(status_code)

        # Import models here to avoid circular imports
        from ..models import MobileMoneyTransaction

        # Use atomic transaction for database updates
        with db_transaction.atomic():
            try:
                # Find the transaction by reference
                txn = MobileMoneyTransaction.objects.select_for_update().filter(
                    provider='airtel_money',
                    transaction_reference=transaction_id
                ).first()

                if not txn:
                    # Try to find by order reference (external_id)
                    order_ref = transaction_data.get('reference')
                    if order_ref:
                        txn = MobileMoneyTransaction.objects.select_for_update().filter(
                            provider='airtel_money',
                            order__number=order_ref
                        ).first()

                if not txn:
                    logger.error(f"Airtel transaction not found: {transaction_id}")
                    WebhookLogger.log_webhook_request('airtel', request, 404, {
                        'transaction_id': transaction_id,
                        'error': 'Transaction not found'
                    })
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Transaction not found'
                    }, status=404)

                # Update transaction status
                txn.status = internal_status
                txn.provider_response = data

                if internal_status == 'successful':
                    txn.completed_at = timezone.now()

                    # Mark order as paid
                    order = txn.order
                    order.payment_verified = True
                    order.payment_verified_at = timezone.now()
                    order.save(update_fields=['payment_verified', 'payment_verified_at'])

                    logger.info(f"Airtel payment successful: {transaction_id} for order {order.number}")

                    # Trigger success actions
                    from ..tasks.celery_tasks import send_payment_confirmed_sms
                    send_payment_confirmed_sms.delay(txn.id)

                elif internal_status == 'failed':
                    txn.error_message = status_message or 'Payment failed'
                    logger.warning(f"Airtel payment failed: {transaction_id} - {status_message}")

                txn.save()

                # Mark as processed (idempotency)
                WebhookIdempotency.mark_processed('airtel', event_id)

                # Log successful processing
                WebhookLogger.log_webhook_request('airtel', request, 200, {
                    'transaction_id': txn.id,
                    'order_number': order.number if internal_status == 'successful' else None,
                    'status': internal_status,
                })

                return JsonResponse({
                    'status': 'success',
                    'message': 'Webhook processed',
                    'transaction_id': str(txn.id)
                })

            except Exception as e:
                logger.error(f"Error processing Airtel transaction: {e}", exc_info=True)
                WebhookLogger.log_webhook_error('airtel', e, request)
                return JsonResponse({
                    'status': 'error',
                    'message': 'Processing error'
                }, status=500)

    except json.JSONDecodeError:
        logger.error("Airtel webhook invalid JSON")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)

    except Exception as e:
        logger.error(f"Airtel webhook error: {e}", exc_info=True)
        WebhookLogger.log_webhook_error('airtel', e, request)
        return JsonResponse({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)


# =============================================================================
# URL CONFIGURATION
# =============================================================================

"""
Add to your Django urls.py:

from django.urls import path
from uganda.webhooks import mobile_money_webhooks_v2

urlpatterns = [
    path(
        'api/webhooks/mtn-momo/',
        mobile_money_webhooks_v2.mtn_momo_callback,
        name='mtn-momo-webhook'
    ),
    path(
        'api/webhooks/airtel-money/',
        mobile_money_webhooks_v2.airtel_money_callback,
        name='airtel-money-webhook'
    ),
]
"""
