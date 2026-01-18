"""
Webhook Handlers for Mobile Money Payment Callbacks
Create Django views/endpoints for these webhooks
"""

import json
import hmac
import hashlib
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone

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
    """
    try:
        # Parse request body
        body = request.body.decode('utf-8')
        data = json.loads(body)

        logger.info(f"MTN MoMo callback received: {data}")

        # Verify signature (if MTN provides one)
        # signature = request.headers.get('X-Callback-Signature')
        # if not verify_mtn_signature(body, signature):
        #     logger.error("Invalid MTN signature")
        #     return JsonResponse({'error': 'Invalid signature'}, status=401)

        # Extract payment data
        external_id = data.get('externalId')  # Your order reference
        reference_id = data.get('referenceId')  # MTN transaction ID
        status = data.get('status')  # SUCCESSFUL, FAILED, PENDING
        amount = data.get('amount')
        currency = data.get('currency')
        reason = data.get('reason')  # If failed

        # Find the transaction
        from ..models import MobileMoneyTransaction

        try:
            transaction = MobileMoneyTransaction.objects.get(
                transaction_reference=reference_id
            )

            # Update transaction status
            if status == 'SUCCESSFUL':
                transaction.status = 'successful'
                transaction.completed_at = timezone.now()

                # Mark order as paid
                order = transaction.order
                order.payment_verified = True
                order.payment_verified_at = timezone.now()
                order.save()

                # Send confirmation SMS
                from ..tasks.celery_tasks import send_payment_confirmed_sms
                send_payment_confirmed_sms.delay(transaction.id)

            elif status == 'FAILED':
                transaction.status = 'failed'
                transaction.error_message = reason or 'Payment failed'

            # Save provider response
            transaction.provider_response = data
            transaction.save()

            logger.info(f"MTN transaction {reference_id} updated to {status}")

            return JsonResponse({
                'status': 'success',
                'message': 'Webhook processed'
            })

        except MobileMoneyTransaction.DoesNotExist:
            logger.error(f"Transaction not found: {reference_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Transaction not found'
            }, status=404)

    except Exception as e:
        logger.error(f"MTN webhook error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def verify_mtn_signature(payload, signature):
    """
    Verify MTN webhook signature
    (Implement based on MTN's documentation)
    """
    # Get MTN webhook secret from settings
    secret = getattr(settings, 'MTN_MOMO_WEBHOOK_SECRET', '')

    if not secret or not signature:
        return False

    # Calculate expected signature
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


# =============================================================================
# AIRTEL MONEY WEBHOOK
# =============================================================================

@csrf_exempt
@require_POST
def airtel_money_callback(request):
    """
    Handle Airtel Money payment callback
    URL: /api/webhooks/airtel-money/
    """
    try:
        # Parse request body
        body = request.body.decode('utf-8')
        data = json.loads(body)

        logger.info(f"Airtel Money callback received: {data}")

        # Extract payment data (adjust based on Airtel's format)
        transaction_id = data.get('transaction', {}).get('id')
        status_code = data.get('status', {}).get('code')  # TS, TF, TA, TIP
        status_message = data.get('status', {}).get('message')

        # Map Airtel status codes
        status_map = {
            'TS': 'successful',  # Transaction Successful
            'TF': 'failed',       # Transaction Failed
            'TA': 'pending',      # Transaction Ambiguous
            'TIP': 'pending',     # Transaction In Progress
        }

        status = status_map.get(status_code, 'pending')

        # Find the transaction
        from ..models import MobileMoneyTransaction

        try:
            # You might need to find by order reference if Airtel doesn't return your transaction ID
            # Or store Airtel's transaction ID when you initiate the payment
            transaction = MobileMoneyTransaction.objects.filter(
                provider='airtel_money',
                transaction_reference=transaction_id
            ).first()

            if not transaction:
                # Try to find by order reference in metadata
                logger.error(f"Airtel transaction not found: {transaction_id}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Transaction not found'
                }, status=404)

            # Update transaction status
            transaction.status = status

            if status == 'successful':
                transaction.completed_at = timezone.now()

                # Mark order as paid
                order = transaction.order
                order.payment_verified = True
                order.payment_verified_at = timezone.now()
                order.save()

                # Send confirmation SMS
                from ..tasks.celery_tasks import send_payment_confirmed_sms
                send_payment_confirmed_sms.delay(transaction.id)

            elif status == 'failed':
                transaction.error_message = status_message

            # Save provider response
            transaction.provider_response = data
            transaction.save()

            logger.info(f"Airtel transaction {transaction_id} updated to {status}")

            return JsonResponse({
                'status': 'success',
                'message': 'Webhook processed'
            })

        except Exception as e:
            logger.error(f"Error processing Airtel transaction: {e}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    except Exception as e:
        logger.error(f"Airtel webhook error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# =============================================================================
# URL CONFIGURATION
# Add to your Django urls.py
# =============================================================================

"""
from django.urls import path
from uganda.webhooks import mobile_money_webhooks

urlpatterns = [
    path(
        'api/webhooks/mtn-momo/',
        mobile_money_webhooks.mtn_momo_callback,
        name='mtn-momo-webhook'
    ),
    path(
        'api/webhooks/airtel-money/',
        mobile_money_webhooks.airtel_money_callback,
        name='airtel-money-webhook'
    ),
]
"""


# =============================================================================
# TESTING WEBHOOKS LOCALLY
# =============================================================================

"""
To test webhooks locally, you need to expose your local server to the internet.

Option 1: Use ngrok
1. Install ngrok: https://ngrok.com/download
2. Run: ngrok http 8000
3. Use the ngrok URL in your Mobile Money callback configuration:
   https://your-ngrok-url.ngrok.io/api/webhooks/mtn-momo/

Option 2: Use localtunnel
1. Install: npm install -g localtunnel
2. Run: lt --port 8000
3. Use the localtunnel URL

Option 3: Use your production server for testing


TESTING WITH CURL:

# Test MTN callback
curl -X POST http://localhost:8000/api/webhooks/mtn-momo/ \
  -H "Content-Type: application/json" \
  -d '{
    "externalId": "12345",
    "referenceId": "mtn-tx-12345",
    "status": "SUCCESSFUL",
    "amount": "50000",
    "currency": "UGX"
  }'

# Test Airtel callback
curl -X POST http://localhost:8000/api/webhooks/airtel-money/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction": {"id": "airtel-tx-12345"},
    "status": {"code": "TS", "message": "Success"}
  }'
"""


# =============================================================================
# WEBHOOK LOGGING
# =============================================================================

class WebhookLog:
    """Log all webhook requests for debugging"""

    @staticmethod
    def log_request(provider, request, response_status):
        """Log webhook request details"""
        from ..models import MobileMoneyTransaction

        try:
            body = request.body.decode('utf-8')

            logger.info(f"""
            Webhook Received:
            Provider: {provider}
            Method: {request.method}
            Headers: {dict(request.headers)}
            Body: {body}
            Response Status: {response_status}
            """)

            # Optionally save to database for audit
            # WebhookLogModel.objects.create(
            #     provider=provider,
            #     request_body=body,
            #     response_status=response_status,
            #     headers=dict(request.headers)
            # )

        except Exception as e:
            logger.error(f"Error logging webhook: {e}")


# =============================================================================
# WEBHOOK SECURITY
# =============================================================================

def validate_webhook_ip(request, allowed_ips):
    """
    Validate that webhook request comes from allowed IPs
    (Get allowed IPs from Mobile Money provider documentation)
    """
    client_ip = get_client_ip(request)

    if client_ip not in allowed_ips:
        logger.warning(f"Webhook from unauthorized IP: {client_ip}")
        return False

    return True


def get_client_ip(request):
    """Get real client IP (handles proxies)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


# =============================================================================
# WEBHOOK RETRY MECHANISM
# =============================================================================

def handle_webhook_failure(transaction_id, error_message):
    """
    Handle webhook processing failure
    Retry checking payment status manually
    """
    from ..tasks.celery_tasks import check_pending_mobile_money_payments

    logger.error(f"Webhook failed for transaction {transaction_id}: {error_message}")

    # Schedule immediate status check
    check_pending_mobile_money_payments.apply_async(countdown=60)  # Check in 1 minute
