"""
Mobile Money Payment Integration for Uganda
Supports MTN Mobile Money and Airtel Money APIs

Production-ready implementation with:
- Automatic retry logic with exponential backoff
- OAuth token caching to reduce API calls
- Idempotency key support
- Structured error handling
- Comprehensive logging
"""

from __future__ import annotations

import base64
import logging
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from .http_client import PaymentAPIError, RetryingSession, new_idempotency_key


logger = logging.getLogger(__name__)


class MobileMoneyError(PaymentAPIError):
    """Base exception for Mobile Money errors"""
    pass


@dataclass
class MTNMoMoConfig:
    """MTN MoMo configuration"""
    base_url: str                  # e.g. "https://sandbox.momodeveloper.mtn.com"
    subscription_key: str          # Ocp-Apim-Subscription-Key
    api_user: str                  # X-Reference-Id user (or provided by portal)
    api_key: str                   # generated API key for that user
    target_environment: str        # "sandbox", "mtnuganda", "production"
    callback_url: str              # your webhook endpoint


class MTNMoMoAPI:
    """
    MTN Mobile Money API Integration

    Features:
    - OAuth token caching (tokens cached for 55 minutes)
    - Automatic retries with exponential backoff
    - Idempotency key support
    - Comprehensive error handling
    """

    # Token cache TTL (MTN tokens expire in 1 hour, cache for 55 min)
    TOKEN_CACHE_TTL = 55 * 60

    def __init__(self, cfg: Optional[MTNMoMoConfig] = None, http: Optional[RetryingSession] = None):
        """
        Initialize MTN MoMo API client

        Args:
            cfg: Configuration object (if None, loads from Django settings)
            http: HTTP client with retry logic (if None, creates default)
        """
        if cfg is None:
            # Load from Django settings
            cfg = MTNMoMoConfig(
                base_url=getattr(
                    settings,
                    'MTN_MOMO_API_URL',
                    'https://sandbox.momodeveloper.mtn.com'
                ),
                subscription_key=getattr(settings, 'MTN_MOMO_SUBSCRIPTION_KEY', ''),
                api_user=getattr(settings, 'MTN_MOMO_API_USER', ''),
                api_key=getattr(settings, 'MTN_MOMO_API_KEY', ''),
                target_environment=getattr(settings, 'MTN_MOMO_TARGET_ENV', 'mtnuganda'),
                callback_url=getattr(settings, 'MTN_MOMO_CALLBACK_URL', ''),
            )

        self.cfg = cfg
        self.http = http or RetryingSession()

    def _basic_auth(self) -> str:
        """Generate Basic Auth header value"""
        raw = f"{self.cfg.api_user}:{self.cfg.api_key}".encode("utf-8")
        return base64.b64encode(raw).decode("utf-8")

    def _headers(self, token: Optional[str] = None, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers"""
        h = {
            "Ocp-Apim-Subscription-Key": self.cfg.subscription_key,
            "X-Target-Environment": self.cfg.target_environment,
            "Content-Type": "application/json",
        }
        if token:
            h["Authorization"] = f"Bearer {token}"
        if extra:
            h.update(extra)
        return h

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get OAuth access token with caching

        Args:
            force_refresh: Force getting new token even if cached

        Returns:
            Access token string

        Raises:
            MobileMoneyError: If token request fails
        """
        cache_key = f"mtn_momo_token_{self.cfg.api_user}"

        # Try cache first
        if not force_refresh:
            cached_token = cache.get(cache_key)
            if cached_token:
                logger.debug("Using cached MTN MoMo token")
                return cached_token

        # Get new token
        url = f"{self.cfg.base_url}/collection/token/"
        headers = self._headers(extra={
            "Authorization": f"Basic {self._basic_auth()}",
        })

        logger.info("Requesting new MTN MoMo access token")
        resp = self.http.request("POST", url, headers=headers)

        if resp.status_code not in (200, 201):
            raise MobileMoneyError(
                "Failed to get MTN token",
                resp.status_code,
                resp.data
            )

        token = resp.data.get("access_token")
        if not token:
            raise MobileMoneyError(
                "MTN token response missing access_token",
                resp.status_code,
                resp.data
            )

        # Cache the token
        cache.set(cache_key, token, self.TOKEN_CACHE_TTL)
        logger.info("MTN MoMo token obtained and cached")

        return token

    def request_to_pay(
        self,
        *,
        amount: str,
        currency: str,
        phone_e164: str,            # e.g. "+256700123456" or "256700123456"
        external_id: str,           # your order/payment id
        payer_message: str = "Payment",
        payee_note: str = "Thank you",
        idempotency_key: Optional[str] = None,
    ) -> str:
        """
        Initiates a payment prompt to the user

        Args:
            amount: Amount as string (e.g., "50000")
            currency: Currency code (e.g., "UGX")
            phone_e164: Phone number in E.164 format (+256...) or without +
            external_id: Your unique order/payment ID
            payer_message: Message shown to customer
            payee_note: Note for merchant
            idempotency_key: Optional idempotency key

        Returns:
            MoMo reference ID (X-Reference-Id UUID)

        Raises:
            MobileMoneyError: If payment request fails
        """
        token = self.get_access_token()
        reference_id = str(uuid.uuid4())  # MoMo expects a UUID here

        url = f"{self.cfg.base_url}/collection/v1_0/requesttopay"

        idem = idempotency_key or new_idempotency_key("mtn")

        # Clean phone number (MTN wants digits only, no + or country code sometimes)
        phone_clean = phone_e164.replace("+", "").replace("256", "")

        headers = self._headers(token, extra={
            "X-Reference-Id": reference_id,
            "X-Callback-Url": self.cfg.callback_url,
            "X-Idempotency-Key": idem,
        })

        body = {
            "amount": amount,
            "currency": currency,
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_clean
            },
            "payerMessage": payer_message,
            "payeeNote": payee_note,
        }

        logger.info(f"MTN MoMo: Requesting payment of {amount} {currency} from {phone_e164}")

        resp = self.http.request("POST", url, headers=headers, json_body=body)

        # MoMo often returns 202 Accepted for async processing
        if resp.status_code not in (202, 200, 201):
            logger.error(f"MTN request-to-pay failed: HTTP {resp.status_code} - {resp.data}")
            raise MobileMoneyError(
                "MTN request-to-pay failed",
                resp.status_code,
                resp.data
            )

        logger.info(f"MTN MoMo payment initiated: {reference_id}")
        return reference_id

    def check_transaction_status(self, reference_id: str) -> Dict[str, Any]:
        """
        Check the status of a transaction

        Args:
            reference_id: The reference ID from request_to_pay

        Returns:
            Dict with transaction status and details

        Raises:
            MobileMoneyError: If status check fails
        """
        token = self.get_access_token()
        url = f"{self.cfg.base_url}/collection/v1_0/requesttopay/{reference_id}"
        headers = self._headers(token)

        logger.debug(f"Checking MTN MoMo transaction status: {reference_id}")

        resp = self.http.request("GET", url, headers=headers)

        if resp.status_code != 200:
            logger.error(f"MTN get status failed: HTTP {resp.status_code} - {resp.data}")
            raise MobileMoneyError(
                "MTN get status failed",
                resp.status_code,
                resp.data
            )

        return resp.data


@dataclass
class AirtelMoneyConfig:
    """Airtel Money configuration"""
    base_url: str            # partner API base
    client_id: str
    client_secret: str
    country: str             # e.g. "UG"
    currency: str            # "UGX"
    callback_url: str        # your webhook endpoint


class AirtelMoneyAPI:
    """
    Airtel Money API Integration

    Features:
    - OAuth token caching (tokens cached for 55 minutes)
    - Automatic retries with exponential backoff
    - Idempotency key support
    - Comprehensive error handling
    """

    # Token cache TTL (Airtel tokens expire in 1 hour, cache for 55 min)
    TOKEN_CACHE_TTL = 55 * 60

    def __init__(self, cfg: Optional[AirtelMoneyConfig] = None, http: Optional[RetryingSession] = None):
        """
        Initialize Airtel Money API client

        Args:
            cfg: Configuration object (if None, loads from Django settings)
            http: HTTP client with retry logic (if None, creates default)
        """
        if cfg is None:
            # Load from Django settings
            cfg = AirtelMoneyConfig(
                base_url=getattr(
                    settings,
                    'AIRTEL_MONEY_API_URL',
                    'https://openapiuat.airtel.africa'
                ),
                client_id=getattr(settings, 'AIRTEL_MONEY_CLIENT_ID', ''),
                client_secret=getattr(settings, 'AIRTEL_MONEY_CLIENT_SECRET', ''),
                country=getattr(settings, 'AIRTEL_MONEY_COUNTRY', 'UG'),
                currency=getattr(settings, 'AIRTEL_MONEY_CURRENCY', 'UGX'),
                callback_url=getattr(settings, 'AIRTEL_MONEY_CALLBACK_URL', ''),
            )

        self.cfg = cfg
        self.http = http or RetryingSession()

    def _headers(self, token: Optional[str] = None, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build request headers"""
        h = {"Content-Type": "application/json"}
        if token:
            h["Authorization"] = f"Bearer {token}"
        if extra:
            h.update(extra)
        return h

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get OAuth access token with caching

        Args:
            force_refresh: Force getting new token even if cached

        Returns:
            Access token string

        Raises:
            MobileMoneyError: If token request fails
        """
        cache_key = f"airtel_money_token_{self.cfg.client_id}"

        # Try cache first
        if not force_refresh:
            cached_token = cache.get(cache_key)
            if cached_token:
                logger.debug("Using cached Airtel Money token")
                return cached_token

        # Get new token
        url = f"{self.cfg.base_url}/auth/oauth2/token"
        body = {
            "client_id": self.cfg.client_id,
            "client_secret": self.cfg.client_secret,
            "grant_type": "client_credentials",
        }

        logger.info("Requesting new Airtel Money access token")
        resp = self.http.request("POST", url, headers=self._headers(), json_body=body)

        if resp.status_code not in (200, 201):
            raise MobileMoneyError(
                "Failed to get Airtel token",
                resp.status_code,
                resp.data
            )

        token = resp.data.get("access_token")
        if not token:
            raise MobileMoneyError(
                "Airtel token response missing access_token",
                resp.status_code,
                resp.data
            )

        # Cache the token
        cache.set(cache_key, token, self.TOKEN_CACHE_TTL)
        logger.info("Airtel Money token obtained and cached")

        return token

    def initiate_payment(
        self,
        *,
        amount: str,
        msisdn_e164: str,          # "+256..." or "256..."
        reference: str,            # your order/payment id
        idempotency_key: Optional[str] = None,
        narrative: str = "Payment",
    ) -> Dict[str, Any]:
        """
        Initiate payment request

        Args:
            amount: Amount as string (e.g., "50000")
            msisdn_e164: Phone number in E.164 format or without +
            reference: Your unique order/payment ID
            idempotency_key: Optional idempotency key
            narrative: Description shown to customer

        Returns:
            Full response dict from Airtel API

        Raises:
            MobileMoneyError: If payment initiation fails
        """
        token = self.get_access_token()
        url = f"{self.cfg.base_url}/merchant/v1/payments/"
        idem = idempotency_key or new_idempotency_key("airtel")

        # Clean phone number (remove +)
        phone_clean = msisdn_e164.replace("+", "")

        body = {
            "reference": reference,
            "subscriber": {
                "country": self.cfg.country,
                "currency": self.cfg.currency,
                "msisdn": phone_clean,
            },
            "transaction": {
                "amount": amount,
                "country": self.cfg.country,
                "currency": self.cfg.currency,
                "id": reference,
            },
            "narrative": narrative,
        }

        if self.cfg.callback_url:
            body["callback_url"] = self.cfg.callback_url

        logger.info(f"Airtel Money: Initiating payment of {amount} {self.cfg.currency} from {msisdn_e164}")

        resp = self.http.request("POST", url, headers=self._headers(token, extra={
            "X-Idempotency-Key": idem,
        }), json_body=body)

        if resp.status_code not in (200, 201, 202):
            logger.error(f"Airtel initiate payment failed: HTTP {resp.status_code} - {resp.data}")
            raise MobileMoneyError(
                "Airtel initiate payment failed",
                resp.status_code,
                resp.data
            )

        logger.info(f"Airtel Money payment initiated: {reference}")
        return resp.data

    def check_transaction_status(self, reference: str) -> Dict[str, Any]:
        """
        Query transaction status

        Args:
            reference: The reference/transaction ID to query

        Returns:
            Full response dict from Airtel API

        Raises:
            MobileMoneyError: If query fails
        """
        token = self.get_access_token()
        url = f"{self.cfg.base_url}/merchant/v1/payments/{reference}"

        logger.debug(f"Checking Airtel Money transaction status: {reference}")

        resp = self.http.request("GET", url, headers=self._headers(token))

        if resp.status_code != 200:
            logger.error(f"Airtel query status failed: HTTP {resp.status_code} - {resp.data}")
            raise MobileMoneyError(
                "Airtel query status failed",
                resp.status_code,
                resp.data
            )

        return resp.data


class MobileMoneyService:
    """
    Unified Mobile Money Service
    Handles both MTN and Airtel Money with backward compatibility

    Features:
    - Provider-agnostic interface
    - Automatic phone number validation and formatting
    - Amount validation
    - Comprehensive error handling
    """

    def __init__(self):
        """Initialize service with both providers"""
        self.mtn = MTNMoMoAPI()
        self.airtel = AirtelMoneyAPI()

    @staticmethod
    def validate_phone_number(phone_number: str) -> str:
        """
        Validate and format Uganda phone number

        Args:
            phone_number: Phone number in various formats

        Returns:
            Formatted phone number (256XXXXXXXXX)

        Raises:
            MobileMoneyError: If phone number is invalid
        """
        # Remove common separators
        phone = phone_number.replace(' ', '').replace('-', '').replace('+', '')

        # Add country code if missing
        if phone.startswith('0'):
            phone = '256' + phone[1:]
        elif not phone.startswith('256'):
            phone = '256' + phone

        # Validate format
        if not phone.startswith('256') or len(phone) != 12:
            raise MobileMoneyError(
                f"Invalid Uganda phone number format: {phone_number}. "
                f"Expected format: 256XXXXXXXXX or +256XXXXXXXXX"
            )

        return phone

    @staticmethod
    def validate_amount(amount: Decimal) -> None:
        """
        Validate payment amount

        Args:
            amount: Amount to validate

        Raises:
            MobileMoneyError: If amount is invalid
        """
        if amount <= 0:
            raise MobileMoneyError("Amount must be greater than zero")

        # MTN/Airtel minimums (adjust based on provider requirements)
        if amount < Decimal('100'):
            raise MobileMoneyError("Amount must be at least 100 UGX")

    def initiate_payment(
        self,
        provider: str,
        phone_number: str,
        amount: Decimal,
        order_number: str,
        payer_message: str = "Payment for your order"
    ) -> Tuple[str, Dict]:
        """
        Initiate a mobile money payment

        Args:
            provider: 'mtn_momo' or 'airtel_money'
            phone_number: Uganda phone number (256XXXXXXXXX or +256XXXXXXXXX)
            amount: Amount in UGX
            order_number: Order reference
            payer_message: Message to show customer

        Returns:
            Tuple of (transaction_id, response_data)

        Raises:
            MobileMoneyError: If validation fails or payment initiation fails
        """
        # Validate inputs
        phone_clean = self.validate_phone_number(phone_number)
        self.validate_amount(amount)

        try:
            if provider == 'mtn_momo':
                reference_id = self.mtn.request_to_pay(
                    amount=str(amount),
                    currency="UGX",
                    phone_e164=phone_clean,
                    external_id=order_number,
                    payer_message=payer_message,
                )
                return reference_id, {'status': 'pending', 'reference_id': reference_id}

            elif provider == 'airtel_money':
                response_data = self.airtel.initiate_payment(
                    amount=str(amount),
                    msisdn_e164=phone_clean,
                    reference=order_number,
                    narrative=payer_message,
                )
                return order_number, response_data

            else:
                raise MobileMoneyError(f"Unsupported provider: {provider}")

        except MobileMoneyError:
            raise
        except Exception as e:
            logger.error(f"Mobile money payment initiation failed: {e}")
            raise MobileMoneyError(f"Payment initiation failed: {str(e)}")

    def check_payment_status(
        self,
        provider: str,
        transaction_id: str
    ) -> Dict:
        """
        Check payment status

        Args:
            provider: 'mtn_momo' or 'airtel_money'
            transaction_id: Transaction ID from initiation

        Returns:
            Dict with status information

        Raises:
            MobileMoneyError: If status check fails
        """
        try:
            if provider == 'mtn_momo':
                return self.mtn.check_transaction_status(transaction_id)
            elif provider == 'airtel_money':
                return self.airtel.check_transaction_status(transaction_id)
            else:
                raise MobileMoneyError(f"Unsupported provider: {provider}")

        except MobileMoneyError:
            raise
        except Exception as e:
            logger.error(f"Mobile money status check failed: {e}")
            raise MobileMoneyError(f"Status check failed: {str(e)}")

    def verify_payment(
        self,
        provider: str,
        transaction_id: str
    ) -> bool:
        """
        Verify if payment was successful

        Args:
            provider: Provider name
            transaction_id: Transaction ID

        Returns:
            True if payment successful, False otherwise
        """
        try:
            status_data = self.check_payment_status(provider, transaction_id)

            # MTN status codes
            if provider == 'mtn_momo':
                status = status_data.get('status', '').upper()
                return status == 'SUCCESSFUL'

            # Airtel status codes
            elif provider == 'airtel_money':
                status_code = status_data.get('status', {}).get('code', '')
                return status_code == 'TS'  # Transaction Successful

            return False

        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            return False


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
Example 1: Basic Usage with MobileMoneyService (Recommended)
-------------------------------------------------------------

from decimal import Decimal
from services.mobile_money import MobileMoneyService, MobileMoneyError

# Initialize service
service = MobileMoneyService()

try:
    # Initiate MTN Mobile Money payment
    transaction_id, response = service.initiate_payment(
        provider='mtn_momo',
        phone_number='0700123456',  # Various formats accepted
        amount=Decimal('50000'),
        order_number='ORD-12345',
        payer_message='Payment for iPhone 14'
    )

    print(f"Payment initiated: {transaction_id}")

    # Check payment status
    status = service.check_payment_status('mtn_momo', transaction_id)
    print(f"Payment status: {status}")

    # Verify payment
    is_paid = service.verify_payment('mtn_momo', transaction_id)
    if is_paid:
        print("Payment successful!")

except MobileMoneyError as e:
    print(f"Payment error: {e}")
    if e.status_code:
        print(f"HTTP Status: {e.status_code}")
    if e.payload:
        print(f"Details: {e.payload}")


Example 2: Direct API Usage with Custom Configuration
------------------------------------------------------

from services.mobile_money import MTNMoMoAPI, MTNMoMoConfig, AirtelMoneyAPI, AirtelMoneyConfig

# Custom MTN MoMo configuration
mtn_cfg = MTNMoMoConfig(
    base_url="https://sandbox.momodeveloper.mtn.com",
    subscription_key="your_subscription_key",
    api_user="your_api_user",
    api_key="your_api_key",
    target_environment="mtnuganda",
    callback_url="https://yoursite.com/webhooks/mtn/"
)

mtn = MTNMoMoAPI(cfg=mtn_cfg)

# Initiate payment
reference_id = mtn.request_to_pay(
    amount="50000",
    currency="UGX",
    phone_e164="+256700123456",
    external_id="ORD-12345",
    payer_message="Pay for order",
)

print(f"MTN Reference: {reference_id}")

# Check status
status = mtn.check_transaction_status(reference_id)
print(f"Status: {status.get('status')}")


Example 3: Airtel Money Direct Usage
-------------------------------------

from services.mobile_money import AirtelMoneyAPI, AirtelMoneyConfig

airtel_cfg = AirtelMoneyConfig(
    base_url="https://openapiuat.airtel.africa",
    client_id="your_client_id",
    client_secret="your_client_secret",
    country="UG",
    currency="UGX",
    callback_url="https://yoursite.com/webhooks/airtel/"
)

airtel = AirtelMoneyAPI(cfg=airtel_cfg)

# Initiate payment
response = airtel.initiate_payment(
    amount="50000",
    msisdn_e164="+256750123456",
    reference="ORD-12345",
    narrative="Payment for order"
)

print(f"Airtel Response: {response}")


Example 4: Phone Number Validation
-----------------------------------

from services.mobile_money import MobileMoneyService

service = MobileMoneyService()

# All these formats work:
phone1 = service.validate_phone_number("0700123456")     # -> "256700123456"
phone2 = service.validate_phone_number("256700123456")   # -> "256700123456"
phone3 = service.validate_phone_number("+256700123456")  # -> "256700123456"
phone4 = service.validate_phone_number("0750-123-456")   # -> "256750123456"


Example 5: Error Handling
--------------------------

from services.mobile_money import MobileMoneyService, MobileMoneyError

service = MobileMoneyService()

try:
    transaction_id, _ = service.initiate_payment(
        provider='mtn_momo',
        phone_number='0700123456',
        amount=Decimal('50000'),
        order_number='ORD-12345'
    )
except MobileMoneyError as e:
    if e.status_code == 401:
        print("Authentication failed - check API credentials")
    elif e.status_code == 429:
        print("Rate limit exceeded - retry later")
    elif e.status_code in (500, 502, 503):
        print("Provider server error - will auto-retry")
    else:
        print(f"Payment failed: {e}")


Example 6: Token Caching
-------------------------

from services.mobile_money import MTNMoMoAPI

mtn = MTNMoMoAPI()

# First call: Gets new token and caches it
token1 = mtn.get_access_token()  # API call made

# Second call: Uses cached token (no API call)
token2 = mtn.get_access_token()  # Returns cached value

# Force refresh
token3 = mtn.get_access_token(force_refresh=True)  # New API call
"""
