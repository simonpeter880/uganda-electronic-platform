# Sentry Quick Start Guide

## ✅ Your Sentry is Configured!

**Your DSN:** `https://68c39713504f50f3b3bfc3210b010abb@o4510729613082624.ingest.de.sentry.io/4510729615376464`

**Region:** Germany (de)

---

## 🚀 Quick Setup (5 minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup-sentry.sh
```

This will:
- ✅ Install Sentry SDK for backend
- ✅ Install Sentry SDK for frontend
- ✅ Verify configuration
- ✅ Run backend test to send test events

### Option 2: Manual Setup

**Backend:**
```bash
cd uganda-backend-code
pip install -r requirements-sentry.txt
python test_sentry.py
```

**Frontend:**
```bash
cd storefront-uganda
pnpm add @sentry/nextjs
pnpm dev
```

---

## 📊 View Your Events

**Sentry Dashboard:**
1. Go to https://sentry.io/
2. Select your project
3. View Issues, Performance, Releases

**Direct Links:**
- Issues: `https://sentry.io/organizations/YOUR_ORG/issues/`
- Performance: `https://sentry.io/organizations/YOUR_ORG/performance/`

---

## 🧪 Testing Sentry

### Backend Test (Already Created)

```bash
cd uganda-backend-code
python test_sentry.py
```

This sends:
- ✅ Info message
- ✅ Test exception (division by zero)
- ✅ Payment error with context
- ✅ SMS error with context
- ✅ Performance transaction

### Frontend Test

Add this to any page to test:

```typescript
import { captureCheckoutError } from '@/lib/sentry';

// Test error capture
try {
  throw new Error('Test error from frontend');
} catch (error) {
  captureCheckoutError(error as Error, { test: true });
}
```

---

## 📁 Files Created

**Configuration:**
- ✅ `.env.development` - Development environment with Sentry
- ✅ `.env.production.example` - Updated with Sentry config
- ✅ `storefront-uganda/.env.local` - Frontend Sentry config

**Backend:**
- ✅ `uganda-backend-code/sentry_config.py` - Sentry integration
- ✅ `uganda-backend-code/requirements-sentry.txt` - Dependencies
- ✅ `uganda-backend-code/test_sentry.py` - Test script

**Frontend:**
- ✅ `storefront-uganda/src/lib/sentry.ts` - Sentry helpers
- ✅ `storefront-uganda/sentry.client.config.ts` - Client config
- ✅ `storefront-uganda/sentry.server.config.ts` - Server config
- ✅ `storefront-uganda/sentry.edge.config.ts` - Edge config

**Scripts:**
- ✅ `setup-sentry.sh` - Automated setup script

---

## 🔧 Environment Variables Set

### Backend (.env.development)
```bash
SENTRY_DSN=https://68c39713504f50f3b3bfc3210b010abb@o4510729613082624.ingest.de.sentry.io/4510729615376464
SENTRY_ENVIRONMENT=development
SENTRY_RELEASE=uganda-electronics@dev
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_SENTRY_DSN=https://68c39713504f50f3b3bfc3210b010abb@o4510729613082624.ingest.de.sentry.io/4510729615376464
NEXT_PUBLIC_SENTRY_ENVIRONMENT=development
NEXT_PUBLIC_SENTRY_RELEASE=storefront@dev
NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

## 💡 Usage Examples

### Backend: Capture Payment Error

```python
from uganda_backend_code.sentry_config import capture_payment_error

try:
    result = process_mtn_payment(...)
except Exception as e:
    capture_payment_error(
        provider='mtn_momo',
        error_message=str(e),
        context={'order_id': order.id}
    )
    raise
```

### Backend: Trace Performance

```python
from uganda_backend_code.sentry_config import trace_payment_transaction

@trace_payment_transaction('mtn_momo')
def process_payment(order_id, amount):
    # Your payment logic here
    return result
```

### Frontend: Capture Checkout Error

```typescript
import { captureCheckoutError } from '@/lib/sentry';

try {
  await createCheckout(items);
} catch (error) {
  captureCheckoutError(error as Error, {
    itemCount: items.length,
    totalAmount: calculateTotal(items)
  });
  throw error;
}
```

### Frontend: Capture Payment Error

```typescript
import { capturePaymentError } from '@/lib/sentry';

try {
  await initiatePayment('mtn_momo', phone, amount);
} catch (error) {
  capturePaymentError('mtn_momo', error as Error, {
    amount,
    phoneHash: hashPhone(phone)
  });
  throw error;
}
```

---

## 🎯 What Sentry Will Monitor

**Automatically Tracked:**
- ✅ All uncaught exceptions
- ✅ API errors (backend)
- ✅ GraphQL errors (frontend)
- ✅ Database query performance
- ✅ Celery task failures
- ✅ Redis connection issues
- ✅ Page load performance
- ✅ API call performance

**Custom Tracking:**
- ✅ Payment failures (MTN, Airtel)
- ✅ SMS delivery failures
- ✅ Order processing errors
- ✅ Checkout flow issues
- ✅ User session replays (on errors)

---

## 🔐 Privacy & Security

**Automatically Protected:**
- ✅ Authorization headers filtered
- ✅ API keys removed
- ✅ Passwords filtered
- ✅ Email addresses hashed
- ✅ Phone numbers hashed
- ✅ Credit card data removed
- ✅ Session tokens filtered

**PII is NOT sent to Sentry!**

---

## 📈 Recommended Alerts

Set up these alerts in Sentry:

1. **High Error Rate**
   - Trigger: >10 errors/minute
   - Notify: Slack #alerts

2. **Payment Failures**
   - Trigger: payment_provider tag exists
   - Notify: Slack #payments

3. **API Performance**
   - Trigger: p95 response time >2s
   - Notify: Slack #tech

4. **SMS Failures**
   - Trigger: >5 SMS errors in 10 min
   - Notify: Slack #operations

---

## 🐛 Troubleshooting

### "No events showing in Sentry"

**Check:**
1. Is Sentry DSN correct in environment?
2. Is internet connection working?
3. Run test script: `python test_sentry.py`
4. Check browser console for errors

### "Sentry not initialized"

**Backend:**
```python
# Add to saleor/settings.py
from uganda_backend_code.sentry_config import init_sentry
init_sentry()
```

**Frontend:**
```typescript
// Already configured in sentry.*.config.ts files
```

### "Too many events"

Adjust sample rates in environment:
```bash
SENTRY_TRACES_SAMPLE_RATE=0.05  # Reduce to 5%
NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE=0.05
```

---

## 📚 Full Documentation

For complete documentation, see:
- [SENTRY_SETUP.md](SENTRY_SETUP.md) - Complete setup guide
- [Sentry Docs](https://docs.sentry.io) - Official documentation

---

## ✅ Verification Checklist

After setup:

- [ ] Backend Sentry installed (`pip list | grep sentry`)
- [ ] Frontend Sentry installed (`pnpm list @sentry/nextjs`)
- [ ] Test script runs successfully
- [ ] Events appear in Sentry dashboard
- [ ] No errors in logs
- [ ] Privacy filters working (check event details)

---

## 🎉 You're All Set!

Sentry is now monitoring your Uganda Electronics Platform!

**What's Happening:**
- 🔍 All errors are being tracked
- 📊 Performance is being monitored
- 🎥 User sessions are recorded on errors
- 🚨 You'll be notified of critical issues

**Access Your Dashboard:**
https://sentry.io/

---

*Questions? Check SENTRY_SETUP.md for detailed information.*
