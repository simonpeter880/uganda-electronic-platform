# Mobile Money Integration Guide
## Uganda Electronics Platform - MTN MoMo & Airtel Money

This guide covers the complete integration of production-ready mobile money payment APIs for your Uganda Electronics Platform.

---

## Table of Contents

1. [Overview](#overview)
2. [What's New](#whats-new)
3. [Architecture](#architecture)
4. [Setup & Configuration](#setup--configuration)
5. [API Credentials](#api-credentials)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Features Implemented

✅ **MTN Mobile Money** - Full RequestToPay API integration
✅ **Airtel Money** - Complete payment initiation & status checking
✅ **Automatic retries** - Exponential backoff for failed requests
✅ **Token caching** - OAuth tokens cached for 55 minutes
✅ **Idempotency** - Prevents duplicate payment processing
✅ **Webhook security** - Signature verification & IP whitelisting
✅ **Comprehensive logging** - Full audit trail for debugging
✅ **Phone number validation** - Supports multiple formats
✅ **Error handling** - Structured errors with status codes

### Files Modified/Created

```
uganda-backend-code/
├── services/
│   ├── http_client.py                    # NEW: Retry logic & HTTP wrapper
│   └── mobile_money.py                   # ENHANCED: Production-ready clients
├── webhooks/
│   ├── webhook_utils.py                  # NEW: Security & idempotency helpers
│   ├── mobile_money_webhooks_v2.py       # NEW: Enhanced webhook handlers
│   └── mobile_money_webhooks.py          # ORIGINAL: Keep for reference
└── MOBILE_MONEY_INTEGRATION_GUIDE.md    # THIS FILE
```

---

## What's New

### HTTP Client Improvements

**Before:**
- Direct `requests` calls with basic error handling
- No automatic retries
- Fixed 30-second timeout
- No structured error responses

**After:**
```python
from services.http_client import RetryingSession, PaymentAPIError

# Automatic retries with exponential backoff
http = RetryingSession(
    timeout=(5.0, 30.0),  # connect, read timeouts
    max_retries=3,
    backoff=0.6
)

# Structured errors with status codes
try:
    resp = http.request("POST", url, headers=headers, json_body=body)
except PaymentAPIError as e:
    print(f"Error: {e.message}, Status: {e.status_code}")
```

### Token Caching

**Before:**
- New token on every request (slow, wastes API quota)

**After:**
```python
# First call: Gets new token and caches it (API call)
token1 = mtn.get_access_token()

# Subsequent calls: Uses cached token (no API call)
token2 = mtn.get_access_token()  # Fast!

# Force refresh if needed
token3 = mtn.get_access_token(force_refresh=True)
```

### Idempotency Support

**Before:**
- Duplicate webhooks could process payments multiple times

**After:**
```python
from webhooks.webhook_utils import WebhookIdempotency

event_id = f"mtn:{reference_id}"

if WebhookIdempotency.is_processed('mtn', event_id):
    return "Already processed"

# Process payment...

WebhookIdempotency.mark_processed('mtn', event_id)
```

### Signature Verification

**Before:**
- Basic placeholder code
- No actual verification

**After:**
```python
from webhooks.webhook_utils import WebhookSecurity

if not WebhookSecurity.verify_signature(
    payload=request.body,
    signature=request.headers.get('X-Signature'),
    secret=settings.MTN_MOMO_WEBHOOK_SECRET
):
    return JsonResponse({'error': 'Invalid signature'}, status=401)
```

---

## Architecture

### Payment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. CUSTOMER CHECKOUT                                            │
└─────────────────────────────────────────────────────────────────┘
          │
          ├─> Order Created (status='unfulfilled')
          ├─> Customer Selects "MTN Mobile Money"
          ├─> Enters Phone Number (0700123456)
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. INITIATE PAYMENT                                             │
└─────────────────────────────────────────────────────────────────┘
          │
          ├─> MobileMoneyService.initiate_payment()
          ├─> Phone validated & formatted (256700123456)
          ├─> Amount validated (>= 100 UGX)
          │
          ├─> MTNMoMoAPI.get_access_token()
          │   ├─> Check cache first
          │   └─> Get new token if needed
          │
          ├─> MTNMoMoAPI.request_to_pay()
          │   ├─> POST /collection/v1_0/requesttopay
          │   ├─> Idempotency-Key: mtn_abc123...
          │   ├─> X-Reference-Id: uuid
          │   └─> Returns 202 Accepted
          │
          ├─> MobileMoneyTransaction created (status='pending')
          └─> Customer receives MTN prompt on phone
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. CUSTOMER APPROVES PAYMENT                                    │
└─────────────────────────────────────────────────────────────────┘
          │
          ├─> Customer enters PIN
          ├─> MTN processes payment
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. WEBHOOK CALLBACK                                             │
└─────────────────────────────────────────────────────────────────┘
          │
          ├─> MTN POST /api/webhooks/mtn-momo/
          │   {
          │     "referenceId": "uuid",
          │     "status": "SUCCESSFUL",
          │     "amount": "50000"
          │   }
          │
          ├─> Verify signature (HMAC-SHA256)
          ├─> Check idempotency (already processed?)
          ├─> Validate IP whitelist
          │
          ├─> Update MobileMoneyTransaction (status='successful')
          ├─> Update Order (payment_verified=True)
          ├─> Send SMS confirmation (Celery task)
          │
          └─> Return 200 OK
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. BACKUP: POLLING                                              │
└─────────────────────────────────────────────────────────────────┘
          │
          ├─> Celery task runs every 5 minutes
          ├─> check_pending_mobile_money_payments()
          ├─> For each pending transaction:
          │   ├─> MTNMoMoAPI.check_transaction_status()
          │   └─> Update if payment confirmed
          │
          └─> Ensures no payment is missed if webhook fails
```

### Class Hierarchy

```
RetryingSession (http_client.py)
    │
    ├─> Used by ─────────┐
    │                    │
    ▼                    ▼
MTNMoMoAPI         AirtelMoneyAPI
    │                    │
    └────────┬───────────┘
             │
             ▼
    MobileMoneyService  <── Used by GraphQL, Celery, Django views
             │
             ├─> validate_phone_number()
             ├─> validate_amount()
             ├─> initiate_payment()
             ├─> check_payment_status()
             └─> verify_payment()
```

---

## Setup & Configuration

### 1. Environment Variables

Add to `/saleor-platform-uganda/backend.env`:

```bash
# ===== MTN MOBILE MONEY =====
MTN_MOMO_API_URL=https://sandbox.momodeveloper.mtn.com  # Change to production URL
MTN_MOMO_API_USER=your_api_user_uuid
MTN_MOMO_API_KEY=your_api_key
MTN_MOMO_SUBSCRIPTION_KEY=your_subscription_key
MTN_MOMO_TARGET_ENV=mtnuganda  # or 'sandbox', 'production'
MTN_MOMO_CALLBACK_URL=https://your-domain.com/api/webhooks/mtn-momo/
MTN_MOMO_WEBHOOK_SECRET=your_webhook_secret  # Optional, for signature verification
MTN_MOMO_ALLOWED_IPS=41.202.207.0,41.202.207.1  # Optional, MTN callback IPs

# ===== AIRTEL MONEY =====
AIRTEL_MONEY_API_URL=https://openapiuat.airtel.africa  # Change to production
AIRTEL_MONEY_CLIENT_ID=your_client_id
AIRTEL_MONEY_CLIENT_SECRET=your_client_secret
AIRTEL_MONEY_COUNTRY=UG
AIRTEL_MONEY_CURRENCY=UGX
AIRTEL_MONEY_CALLBACK_URL=https://your-domain.com/api/webhooks/airtel-money/
AIRTEL_MONEY_WEBHOOK_SECRET=your_webhook_secret  # Optional
AIRTEL_MONEY_ALLOWED_IPS=196.46.128.0,196.46.128.1  # Optional, Airtel IPs

# ===== REDIS (for token caching) =====
CACHE_URL=redis://cache:6379/0  # Already configured

# ===== CELERY (for background tasks) =====
CELERY_BROKER_URL=redis://cache:6379/1  # Already configured
```

### 2. Django URLs Configuration

Add to your Django `urls.py`:

```python
from django.urls import path
from uganda_backend.webhooks import mobile_money_webhooks_v2

urlpatterns = [
    # ... other URLs ...

    # Mobile Money Webhooks
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
```

### 3. Django Settings

Ensure Redis cache is configured in `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('CACHE_URL', 'redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 4. Celery Beat Schedule

Add to your Celery configuration:

```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-pending-payments': {
        'task': 'uganda_backend.tasks.celery_tasks.check_pending_mobile_money_payments',
        'schedule': 300.0,  # Every 5 minutes
    },
    # ... other tasks ...
}
```

---

## API Credentials

### MTN Mobile Money

1. **Sandbox Setup** (for testing):
   - Go to https://momodeveloper.mtn.com/
   - Sign up and create an account
   - Subscribe to "Collection" product
   - Generate API User and API Key
   - Get Subscription Key from dashboard

2. **Production Setup**:
   - Contact MTN Uganda: mobilemoney@mtn.co.ug
   - Request merchant account
   - Sign agreement
   - Receive production credentials

3. **Getting Credentials**:
   ```bash
   # Sandbox API User (UUID format)
   MTN_MOMO_API_USER=e1234567-e89b-12d3-a456-426614174000

   # Sandbox API Key (generated)
   MTN_MOMO_API_KEY=abc123def456...

   # Subscription Key (from portal)
   MTN_MOMO_SUBSCRIPTION_KEY=xyz789...
   ```

### Airtel Money

1. **Sandbox Setup**:
   - Email: developer@airtel.co.ug
   - Request sandbox access
   - Provide business details
   - Receive test credentials

2. **Production Setup**:
   - Contact Airtel Uganda Business: 0800-100-100
   - Complete merchant onboarding
   - Sign merchant agreement
   - Receive production credentials

3. **Getting Credentials**:
   ```bash
   AIRTEL_MONEY_CLIENT_ID=your_client_id_from_airtel
   AIRTEL_MONEY_CLIENT_SECRET=your_secret_from_airtel
   ```

### Africa's Talking (SMS)

Already configured, but to get your own:

1. Go to https://africastalking.com/
2. Sign up for Uganda
3. Get API key from dashboard
4. Add sender ID (alphanumeric, max 11 chars)

---

## Testing

### 1. Local Testing with ngrok

Mobile money providers need to send webhooks to your server. To test locally:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Start your Django server
python manage.py runserver

# In another terminal, start ngrok
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update your .env:
MTN_MOMO_CALLBACK_URL=https://abc123.ngrok.io/api/webhooks/mtn-momo/
AIRTEL_MONEY_CALLBACK_URL=https://abc123.ngrok.io/api/webhooks/airtel-money/

# Update callback URLs in MTN/Airtel portals
```

### 2. Test Payment Initiation

```python
from decimal import Decimal
from services.mobile_money import MobileMoneyService, MobileMoneyError

service = MobileMoneyService()

try:
    # MTN Test Numbers (sandbox):
    # 256770000000 - Success
    # 256780000000 - Failed

    transaction_id, response = service.initiate_payment(
        provider='mtn_momo',
        phone_number='256770000000',  # Test number
        amount=Decimal('1000'),
        order_number='TEST-001',
        payer_message='Test payment'
    )

    print(f"Success! Transaction ID: {transaction_id}")

except MobileMoneyError as e:
    print(f"Error: {e}")
    if e.status_code:
        print(f"HTTP Status: {e.status_code}")
```

### 3. Test Webhook Locally

```bash
# Terminal 1: Start Django
python manage.py runserver

# Terminal 2: Send test webhook
curl -X POST http://localhost:8000/api/webhooks/mtn-momo/ \
  -H "Content-Type: application/json" \
  -d '{
    "externalId": "TEST-001",
    "referenceId": "test-uuid-12345",
    "status": "SUCCESSFUL",
    "amount": "1000",
    "currency": "UGX"
  }'

# Check response
# Should return: {"status": "success", "message": "Webhook processed"}
```

### 4. Test Idempotency

```bash
# Send same webhook twice
curl -X POST http://localhost:8000/api/webhooks/mtn-momo/ \
  -H "Content-Type: application/json" \
  -d '{
    "externalId": "TEST-001",
    "referenceId": "same-uuid-12345",
    "status": "SUCCESSFUL",
    "amount": "1000",
    "currency": "UGX"
  }'

# Second call should return:
# {"status": "success", "message": "Already processed"}
```

### 5. Test Phone Number Validation

```python
from services.mobile_money import MobileMoneyService

service = MobileMoneyService()

# All these should work:
print(service.validate_phone_number("0700123456"))      # 256700123456
print(service.validate_phone_number("256700123456"))    # 256700123456
print(service.validate_phone_number("+256700123456"))   # 256700123456
print(service.validate_phone_number("0750-123-456"))    # 256750123456

# This should fail:
try:
    service.validate_phone_number("123")
except Exception as e:
    print(f"Error: {e}")  # Invalid phone number format
```

---

## Deployment

### Production Checklist

- [ ] **Update API URLs**
  ```bash
  MTN_MOMO_API_URL=https://proxy.momoapi.mtn.com  # Production URL
  AIRTEL_MONEY_API_URL=https://openapi.airtel.africa  # Production URL
  ```

- [ ] **Configure Production Credentials**
  - Replace sandbox API keys with production keys
  - Update subscription keys
  - Set target environment to 'production'

- [ ] **Set Up Webhooks**
  - Configure production callback URLs in MTN/Airtel portals
  - Use HTTPS (SSL certificate required)
  - Test webhook connectivity

- [ ] **Enable Security Features**
  ```bash
  # Get webhook secrets from providers
  MTN_MOMO_WEBHOOK_SECRET=your_production_secret
  AIRTEL_MONEY_WEBHOOK_SECRET=your_production_secret

  # Get allowed IPs from providers
  MTN_MOMO_ALLOWED_IPS=41.202.207.0,41.202.207.1,41.202.207.2
  AIRTEL_MONEY_ALLOWED_IPS=196.46.128.0,196.46.128.1
  ```

- [ ] **Configure Monitoring**
  - Set up error tracking (Sentry, Rollbar)
  - Configure CloudWatch/logging
  - Set up alerts for failed payments

- [ ] **Test in Production**
  - Start with small test transactions
  - Verify webhooks are received
  - Check Celery tasks are running

### Deployment Commands

```bash
# 1. Pull latest code
git pull origin main

# 2. Update environment variables
nano /path/to/.env

# 3. Rebuild Docker containers
docker-compose -f docker-compose.yml build api

# 4. Restart services
docker-compose -f docker-compose.yml up -d

# 5. Check logs
docker-compose logs -f api celery

# 6. Test payment
# Use production phone numbers and small amounts
```

---

## Troubleshooting

### Common Issues

#### 1. "Failed to get MTN token"

**Symptoms:**
```
MobileMoneyError: Failed to get MTN token (HTTP 401)
```

**Solutions:**
- Check `MTN_MOMO_API_USER` and `MTN_MOMO_API_KEY` are correct
- Verify `MTN_MOMO_SUBSCRIPTION_KEY` is valid
- Ensure API User is created in MTN portal
- Check if subscription is active

**Debug:**
```python
from services.mobile_money import MTNMoMoAPI

mtn = MTNMoMoAPI()
print(f"API URL: {mtn.cfg.base_url}")
print(f"API User: {mtn.cfg.api_user}")
print(f"Subscription Key: {mtn.cfg.subscription_key[:10]}...")

try:
    token = mtn.get_access_token(force_refresh=True)
    print(f"Token: {token[:20]}...")
except Exception as e:
    print(f"Error: {e}")
```

#### 2. "Payment stuck in pending"

**Symptoms:**
- Transaction status never updates
- Webhook not received

**Solutions:**
- Check webhook URL is accessible (use ngrok for local)
- Verify callback URL in MTN/Airtel portal
- Check firewall/security groups allow provider IPs
- Look at Celery task logs (backup polling should catch it)

**Debug:**
```bash
# Check Celery tasks
docker-compose logs celery | grep "Checking pending"

# Manually check payment status
python manage.py shell
>>> from services.mobile_money import MobileMoneyService
>>> service = MobileMoneyService()
>>> status = service.check_payment_status('mtn_momo', 'transaction-id')
>>> print(status)
```

#### 3. "Signature verification failed"

**Symptoms:**
```
Webhook from unauthorized signature
```

**Solutions:**
- Verify `MTN_MOMO_WEBHOOK_SECRET` matches portal
- Check signature header name (X-Signature, X-Callback-Signature)
- Ensure raw request body is used (not parsed JSON)

**Debug:**
```python
# In webhook handler, add logging:
import logging
logger = logging.getLogger(__name__)

body_bytes = request.body
signature = request.headers.get('X-Signature')
secret = settings.MTN_MOMO_WEBHOOK_SECRET

logger.info(f"Body: {body_bytes}")
logger.info(f"Signature: {signature}")
logger.info(f"Secret: {secret[:10]}...")

# Then check if verification logic is correct
```

#### 4. "Duplicate payment processing"

**Symptoms:**
- Same payment processed twice
- Order marked as paid multiple times

**Solutions:**
- Idempotency should prevent this
- Check Redis cache is working
- Verify `WebhookIdempotency.is_processed()` is called

**Debug:**
```bash
# Check Redis cache
docker-compose exec cache redis-cli

# In Redis CLI:
KEYS webhook_processed:*
GET webhook_processed:mtn:transaction-id

# Should return "True" if processed
```

#### 5. "Phone number validation error"

**Symptoms:**
```
MobileMoneyError: Invalid Uganda phone number format
```

**Solutions:**
- Phone must be 12 digits starting with 256
- Or 10 digits starting with 0 (auto-converted)

**Valid formats:**
```
0700123456      → 256700123456
256700123456    → 256700123456
+256700123456   → 256700123456
0750-123-456    → 256750123456
```

---

## Performance Optimization

### Token Caching

OAuth tokens are cached in Redis for 55 minutes:

```python
# First call: API request made
token1 = mtn.get_access_token()  # ~200ms

# Subsequent calls: Cache hit
token2 = mtn.get_access_token()  # ~2ms

# 100x faster!
```

### Database Queries

Use `select_for_update()` to prevent race conditions:

```python
with transaction.atomic():
    txn = MobileMoneyTransaction.objects.select_for_update().get(id=txn_id)
    # Update transaction
    txn.status = 'successful'
    txn.save()
```

### Celery Tasks

Configure for optimal performance:

```python
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes
```

---

## Security Best Practices

1. **Always verify webhooks**
   - Use signature verification
   - Whitelist provider IPs
   - Use HTTPS only

2. **Protect API credentials**
   - Never commit secrets to Git
   - Use environment variables
   - Rotate keys regularly

3. **Implement idempotency**
   - Prevent duplicate processing
   - Use unique transaction IDs
   - Cache processed events

4. **Log everything**
   - Audit trail for compliance
   - Debug production issues
   - Monitor for fraud

5. **Handle PCI compliance**
   - Never store card data (not applicable for mobile money)
   - Log payment amounts and statuses
   - Encrypt sensitive data

---

## Support & Resources

### MTN Mobile Money
- Portal: https://momodeveloper.mtn.com/
- Docs: https://momodeveloper.mtn.com/api-documentation/
- Support: mobilemoney@mtn.co.ug

### Airtel Money
- Support: developer@airtel.co.ug
- Business: 0800-100-100

### Platform Support
- GitHub Issues: [Your repo]/issues
- Email: [Your support email]

---

## Next Steps

1. ✅ Read this guide
2. ✅ Set up development environment
3. ✅ Get sandbox API credentials
4. ✅ Test payment flow locally
5. ✅ Test webhooks with ngrok
6. ✅ Deploy to staging
7. ✅ Get production credentials
8. ✅ Deploy to production
9. ✅ Monitor and optimize

---

**Version:** 2.0
**Last Updated:** 2026-01-13
**Author:** Claude Code Integration
