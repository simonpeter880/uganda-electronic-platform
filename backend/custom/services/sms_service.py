"""
SMS Notification Service for Uganda
Uses Africa's Talking SMS API
"""

import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


class SMSError(Exception):
    """Base exception for SMS errors"""
    pass


class AfricasTalkingAPI:
    """Africa's Talking SMS API Integration"""

    def __init__(self):
        self.username = getattr(settings, 'AFRICAS_TALKING_USERNAME', 'sandbox')
        self.api_key = getattr(settings, 'AFRICAS_TALKING_API_KEY', '')
        self.sender_id = getattr(settings, 'AFRICAS_TALKING_SENDER_ID', 'SHOP')

        # Use sandbox for testing, production for live
        if self.username == 'sandbox':
            self.base_url = 'https://api.sandbox.africastalking.com/version1'
        else:
            self.base_url = 'https://api.africastalking.com/version1'

    def send_sms(
        self,
        phone_numbers: List[str],
        message: str,
        sender_id: Optional[str] = None
    ) -> Dict:
        """
        Send SMS to one or more recipients

        Args:
            phone_numbers: List of Uganda phone numbers (256XXXXXXXXX)
            message: SMS message text (max 160 chars for single SMS)
            sender_id: Optional custom sender ID (11 chars max, alphanumeric)

        Returns:
            Dict with response data from Africa's Talking
        """
        url = f"{self.base_url}/messaging"

        headers = {
            'apiKey': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }

        # Join phone numbers with commas
        recipients = ','.join(phone_numbers)

        payload = {
            'username': self.username,
            'to': recipients,
            'message': message,
        }

        # Use custom sender ID if provided, otherwise use default
        if sender_id:
            payload['from'] = sender_id[:11]  # Max 11 characters
        elif self.sender_id:
            payload['from'] = self.sender_id

        try:
            response = requests.post(
                url,
                data=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Africa's Talking response format:
            # {
            #     "SMSMessageData": {
            #         "Message": "Sent to 1/1 Total Cost: UGX 60",
            #         "Recipients": [{
            #             "statusCode": 101,
            #             "number": "+256700123456",
            #             "status": "Success",
            #             "cost": "UGX 60",
            #             "messageId": "ATXid_..."
            #         }]
            #     }
            # }

            logger.info(f"SMS sent successfully: {data.get('SMSMessageData', {}).get('Message')}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Africa's Talking SMS request failed: {e}")
            raise SMSError(f"Failed to send SMS: {str(e)}")

    def fetch_messages(self, last_received_id: int = 0) -> Dict:
        """
        Fetch incoming SMS messages (if you have a short code)

        Args:
            last_received_id: ID of last message received (for pagination)

        Returns:
            Dict with messages
        """
        url = f"{self.base_url}/messaging"

        headers = {
            'apiKey': self.api_key,
            'Accept': 'application/json',
        }

        params = {
            'username': self.username,
            'lastReceivedId': last_received_id,
        }

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch messages: {e}")
            raise SMSError(f"Failed to fetch messages: {str(e)}")


class SMSService:
    """
    SMS Service for Uganda Electronics Platform
    Handles all SMS notifications
    """

    def __init__(self):
        self.api = AfricasTalkingAPI()

    def send_single_sms(
        self,
        phone_number: str,
        message: str,
        sender_id: Optional[str] = None
    ) -> Dict:
        """
        Send SMS to a single recipient

        Args:
            phone_number: Uganda phone number (256XXXXXXXXX)
            message: SMS text
            sender_id: Optional sender ID

        Returns:
            Dict with delivery info
        """
        # Validate phone number
        if not self.is_valid_uganda_phone(phone_number):
            raise SMSError("Invalid Uganda phone number format")

        try:
            result = self.api.send_sms([phone_number], message, sender_id)

            # Extract recipient info
            recipients = result.get('SMSMessageData', {}).get('Recipients', [])
            if recipients:
                recipient = recipients[0]
                return {
                    'success': recipient.get('status') == 'Success',
                    'status_code': recipient.get('statusCode'),
                    'message_id': recipient.get('messageId'),
                    'cost': recipient.get('cost'),
                    'number': recipient.get('number'),
                }
            else:
                raise SMSError("No recipient data in response")

        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            raise

    def send_bulk_sms(
        self,
        phone_numbers: List[str],
        message: str,
        sender_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Send same SMS to multiple recipients

        Args:
            phone_numbers: List of Uganda phone numbers
            message: SMS text
            sender_id: Optional sender ID

        Returns:
            List of dicts with delivery info for each recipient
        """
        # Validate all phone numbers
        valid_numbers = [p for p in phone_numbers if self.is_valid_uganda_phone(p)]

        if not valid_numbers:
            raise SMSError("No valid phone numbers provided")

        try:
            result = self.api.send_sms(valid_numbers, message, sender_id)

            # Extract recipient info
            recipients = result.get('SMSMessageData', {}).get('Recipients', [])
            return [{
                'success': r.get('status') == 'Success',
                'status_code': r.get('statusCode'),
                'message_id': r.get('messageId'),
                'cost': r.get('cost'),
                'number': r.get('number'),
            } for r in recipients]

        except Exception as e:
            logger.error(f"Failed to send bulk SMS: {e}")
            raise

    def send_order_confirmation(
        self,
        phone_number: str,
        order_number: str,
        total_amount: str,
        shop_name: str = "Electronics Shop"
    ) -> Dict:
        """Send order confirmation SMS"""
        message = (
            f"Thank you for your order #{order_number}! "
            f"Total: UGX {total_amount}. "
            f"We'll notify you when it's ready. "
            f"- {shop_name}"
        )
        return self.send_single_sms(phone_number, message)

    def send_payment_confirmation(
        self,
        phone_number: str,
        order_number: str,
        amount: str,
        shop_name: str = "Electronics Shop"
    ) -> Dict:
        """Send payment confirmation SMS"""
        message = (
            f"Payment of UGX {amount} received for order #{order_number}. "
            f"Your order is being processed. "
            f"- {shop_name}"
        )
        return self.send_single_sms(phone_number, message)

    def send_payment_reminder(
        self,
        phone_number: str,
        order_number: str,
        amount_due: str,
        shop_name: str = "Electronics Shop"
    ) -> Dict:
        """Send payment reminder SMS"""
        message = (
            f"Reminder: Payment of UGX {amount_due} pending for order #{order_number}. "
            f"Pay via MTN/Airtel Mobile Money. "
            f"- {shop_name}"
        )
        return self.send_single_sms(phone_number, message)

    def send_ready_for_pickup(
        self,
        phone_number: str,
        order_number: str,
        verification_code: str,
        shop_address: str,
        shop_name: str = "Electronics Shop"
    ) -> Dict:
        """Send ready for pickup notification"""
        message = (
            f"Your order #{order_number} is ready for pickup! "
            f"Code: {verification_code}. "
            f"Location: {shop_address}. "
            f"- {shop_name}"
        )
        return self.send_single_sms(phone_number, message)

    def send_out_for_delivery(
        self,
        phone_number: str,
        order_number: str,
        estimated_time: str,
        shop_name: str = "Electronics Shop"
    ) -> Dict:
        """Send out for delivery notification"""
        message = (
            f"Your order #{order_number} is out for delivery! "
            f"Expected arrival: {estimated_time}. "
            f"- {shop_name}"
        )
        return self.send_single_sms(phone_number, message)

    def send_delivered(
        self,
        phone_number: str,
        order_number: str,
        shop_name: str = "Electronics Shop"
    ) -> Dict:
        """Send delivery confirmation SMS"""
        message = (
            f"Your order #{order_number} has been delivered! "
            f"Thank you for shopping with us. "
            f"- {shop_name}"
        )
        return self.send_single_sms(phone_number, message)

    def send_installment_reminder(
        self,
        phone_number: str,
        order_number: str,
        installment_number: int,
        amount_due: str,
        due_date: str,
        shop_name: str = "Electronics Shop"
    ) -> Dict:
        """Send installment payment reminder"""
        message = (
            f"Reminder: Installment {installment_number} of UGX {amount_due} "
            f"for order #{order_number} is due on {due_date}. "
            f"- {shop_name}"
        )
        return self.send_single_sms(phone_number, message)

    def send_custom_message(
        self,
        phone_number: str,
        message: str,
        sender_id: Optional[str] = None
    ) -> Dict:
        """Send custom SMS message"""
        return self.send_single_sms(phone_number, message, sender_id)

    @staticmethod
    def is_valid_uganda_phone(phone_number: str) -> bool:
        """
        Validate Uganda phone number format
        Format: 256XXXXXXXXX (country code + 9 digits)
        """
        import re
        pattern = r'^256[0-9]{9}$'
        return bool(re.match(pattern, phone_number))

    @staticmethod
    def format_uganda_phone(phone_number: str) -> str:
        """
        Format phone number to Uganda standard (256XXXXXXXXX)

        Handles:
        - +256700123456 -> 256700123456
        - 0700123456 -> 256700123456
        - 256700123456 -> 256700123456 (no change)
        """
        # Remove spaces, dashes, parentheses
        phone = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

        # Remove + prefix
        if phone.startswith('+'):
            phone = phone[1:]

        # Convert 0700... to 256700...
        if phone.startswith('0') and len(phone) == 10:
            phone = '256' + phone[1:]

        # Validate final format
        if SMSService.is_valid_uganda_phone(phone):
            return phone
        else:
            raise SMSError(f"Invalid phone number format: {phone_number}")


# Example usage:
"""
from services.sms_service import SMSService

# Initialize service
sms_service = SMSService()

# Send order confirmation
result = sms_service.send_order_confirmation(
    phone_number='256700123456',
    order_number='ORD-12345',
    total_amount='450,000',
    shop_name='Electronics Uganda'
)

if result['success']:
    print(f"SMS sent! Message ID: {result['message_id']}")
    print(f"Cost: {result['cost']}")
else:
    print(f"SMS failed with code: {result['status_code']}")

# Send custom message
sms_service.send_custom_message(
    phone_number='256700123456',
    message='Special offer: 20% off all smartphones this weekend!',
    sender_id='DEALS'
)

# Format phone number
formatted = SMSService.format_uganda_phone('0700123456')
print(formatted)  # Output: 256700123456
"""
