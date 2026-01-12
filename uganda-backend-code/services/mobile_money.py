"""
Mobile Money Payment Integration for Uganda
Supports MTN Mobile Money and Airtel Money APIs
"""

import requests
import logging
import uuid
from decimal import Decimal
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


class MobileMoneyError(Exception):
    """Base exception for Mobile Money errors"""
    pass


class MTNMoMoAPI:
    """MTN Mobile Money API Integration"""

    def __init__(self):
        self.base_url = getattr(
            settings,
            'MTN_MOMO_API_URL',
            'https://sandbox.momodeveloper.mtn.com'  # Use production URL in live
        )
        self.api_user = getattr(settings, 'MTN_MOMO_API_USER', '')
        self.api_key = getattr(settings, 'MTN_MOMO_API_KEY', '')
        self.subscription_key = getattr(settings, 'MTN_MOMO_SUBSCRIPTION_KEY', '')
        self.callback_url = getattr(settings, 'MTN_MOMO_CALLBACK_URL', '')

    def get_access_token(self) -> str:
        """Get OAuth access token for API calls"""
        url = f"{self.base_url}/collection/token/"

        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
        }

        auth = (self.api_user, self.api_key)

        try:
            response = requests.post(url, headers=headers, auth=auth, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['access_token']
        except requests.exceptions.RequestException as e:
            logger.error(f"MTN MoMo token request failed: {e}")
            raise MobileMoneyError(f"Failed to get access token: {str(e)}")

    def request_to_pay(
        self,
        phone_number: str,
        amount: Decimal,
        reference: str,
        payer_message: str = "Payment for order"
    ) -> Tuple[str, Dict]:
        """
        Request payment from customer

        Args:
            phone_number: Customer's phone number (256XXXXXXXXX)
            amount: Amount in UGX
            reference: Unique reference (order number)
            payer_message: Message shown to payer

        Returns:
            Tuple of (transaction_id, response_data)
        """
        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())

        url = f"{self.base_url}/collection/v1_0/requesttopay"

        # Get access token
        access_token = self.get_access_token()

        headers = {
            'X-Reference-Id': transaction_id,
            'X-Target-Environment': 'mtnuganda',  # or 'mtncameroon', 'mtnivorycoast'
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # Remove '256' prefix for MTN API (they expect without country code)
        phone = phone_number.replace('256', '')

        payload = {
            'amount': str(amount),
            'currency': 'UGX',
            'externalId': reference,
            'payer': {
                'partyIdType': 'MSISDN',
                'partyId': phone,
            },
            'payerMessage': payer_message,
            'payeeNote': f'Payment for {reference}',
        }

        if self.callback_url:
            payload['callback_url'] = self.callback_url

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 202:
                # Request accepted
                logger.info(f"MTN MoMo payment request sent: {transaction_id}")
                return transaction_id, {'status': 'pending', 'message': 'Payment request sent'}
            else:
                error_data = response.json() if response.content else {}
                logger.error(f"MTN MoMo request failed: {response.status_code} - {error_data}")
                raise MobileMoneyError(f"Payment request failed: {error_data.get('message', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            logger.error(f"MTN MoMo request exception: {e}")
            raise MobileMoneyError(f"Payment request failed: {str(e)}")

    def check_transaction_status(self, transaction_id: str) -> Dict:
        """
        Check the status of a transaction

        Args:
            transaction_id: The transaction ID from request_to_pay

        Returns:
            Dict with transaction status
        """
        url = f"{self.base_url}/collection/v1_0/requesttopay/{transaction_id}"

        access_token = self.get_access_token()

        headers = {
            'X-Target-Environment': 'mtnuganda',
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Authorization': f'Bearer {access_token}',
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            return {
                'status': data.get('status'),  # 'PENDING', 'SUCCESSFUL', 'FAILED'
                'amount': data.get('amount'),
                'currency': data.get('currency'),
                'external_id': data.get('externalId'),
                'payer': data.get('payer'),
                'reason': data.get('reason'),  # If failed
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"MTN MoMo status check failed: {e}")
            raise MobileMoneyError(f"Status check failed: {str(e)}")


class AirtelMoneyAPI:
    """Airtel Money API Integration"""

    def __init__(self):
        self.base_url = getattr(
            settings,
            'AIRTEL_MONEY_API_URL',
            'https://openapiuat.airtel.africa'  # Use production URL in live
        )
        self.client_id = getattr(settings, 'AIRTEL_MONEY_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'AIRTEL_MONEY_CLIENT_SECRET', '')
        self.callback_url = getattr(settings, 'AIRTEL_MONEY_CALLBACK_URL', '')

    def get_access_token(self) -> str:
        """Get OAuth access token"""
        url = f"{self.base_url}/auth/oauth2/token"

        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }

        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['access_token']
        except requests.exceptions.RequestException as e:
            logger.error(f"Airtel Money token request failed: {e}")
            raise MobileMoneyError(f"Failed to get access token: {str(e)}")

    def initiate_payment(
        self,
        phone_number: str,
        amount: Decimal,
        reference: str
    ) -> Tuple[str, Dict]:
        """
        Initiate payment request

        Args:
            phone_number: Customer's phone number (256XXXXXXXXX)
            amount: Amount in UGX
            reference: Unique reference

        Returns:
            Tuple of (transaction_id, response_data)
        """
        transaction_id = f"TXN{uuid.uuid4().hex[:16].upper()}"

        url = f"{self.base_url}/merchant/v1/payments/"

        access_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Country': 'UG',
            'X-Currency': 'UGX',
        }

        payload = {
            'reference': transaction_id,
            'subscriber': {
                'country': 'UG',
                'currency': 'UGX',
                'msisdn': phone_number,
            },
            'transaction': {
                'amount': str(amount),
                'country': 'UG',
                'currency': 'UGX',
                'id': reference,
            },
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get('status', {}).get('code') == '200':
                logger.info(f"Airtel Money payment initiated: {transaction_id}")
                return transaction_id, data
            else:
                error_msg = data.get('status', {}).get('message', 'Unknown error')
                logger.error(f"Airtel Money payment failed: {error_msg}")
                raise MobileMoneyError(f"Payment initiation failed: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Airtel Money request exception: {e}")
            raise MobileMoneyError(f"Payment request failed: {str(e)}")

    def check_transaction_status(self, transaction_id: str) -> Dict:
        """Check transaction status"""
        url = f"{self.base_url}/standard/v1/payments/{transaction_id}"

        access_token = self.get_access_token()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Country': 'UG',
            'X-Currency': 'UGX',
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            status_code = data.get('status', {}).get('code')
            status_map = {
                'TS': 'successful',
                'TF': 'failed',
                'TA': 'pending',
                'TIP': 'pending',
            }

            return {
                'status': status_map.get(status_code, 'unknown'),
                'transaction_id': data.get('data', {}).get('transaction', {}).get('id'),
                'message': data.get('status', {}).get('message'),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Airtel Money status check failed: {e}")
            raise MobileMoneyError(f"Status check failed: {str(e)}")


class MobileMoneyService:
    """
    Unified Mobile Money Service
    Handles both MTN and Airtel Money
    """

    def __init__(self):
        self.mtn = MTNMoMoAPI()
        self.airtel = AirtelMoneyAPI()

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
            phone_number: Uganda phone number (256XXXXXXXXX)
            amount: Amount in UGX
            order_number: Order reference
            payer_message: Message to show customer

        Returns:
            Tuple of (transaction_id, response_data)
        """
        # Validate phone number
        if not phone_number.startswith('256') or len(phone_number) != 12:
            raise MobileMoneyError("Invalid Uganda phone number format")

        # Validate amount
        if amount <= 0:
            raise MobileMoneyError("Amount must be greater than zero")

        try:
            if provider == 'mtn_momo':
                return self.mtn.request_to_pay(
                    phone_number,
                    amount,
                    order_number,
                    payer_message
                )
            elif provider == 'airtel_money':
                return self.airtel.initiate_payment(
                    phone_number,
                    amount,
                    order_number
                )
            else:
                raise MobileMoneyError(f"Unsupported provider: {provider}")

        except Exception as e:
            logger.error(f"Mobile money payment initiation failed: {e}")
            raise

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
        """
        try:
            if provider == 'mtn_momo':
                return self.mtn.check_transaction_status(transaction_id)
            elif provider == 'airtel_money':
                return self.airtel.check_transaction_status(transaction_id)
            else:
                raise MobileMoneyError(f"Unsupported provider: {provider}")

        except Exception as e:
            logger.error(f"Mobile money status check failed: {e}")
            raise

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
            status = status_data.get('status', '').upper()
            return status in ['SUCCESSFUL', 'TS', 'successful']
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            return False


# Example usage:
"""
from services.mobile_money import MobileMoneyService

# Initialize service
momo_service = MobileMoneyService()

# Initiate MTN Mobile Money payment
transaction_id, response = momo_service.initiate_payment(
    provider='mtn_momo',
    phone_number='256700123456',
    amount=Decimal('50000'),
    order_number='ORD-12345',
    payer_message='Payment for iPhone 14'
)

# Check payment status
status = momo_service.check_payment_status('mtn_momo', transaction_id)
print(f"Payment status: {status['status']}")

# Verify payment
is_paid = momo_service.verify_payment('mtn_momo', transaction_id)
if is_paid:
    print("Payment successful!")
"""
