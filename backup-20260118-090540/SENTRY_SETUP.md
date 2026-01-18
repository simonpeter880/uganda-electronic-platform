# Sentry Setup Guide

This guide explains how to set up Sentry for error tracking and performance monitoring in the Uganda Electronics Platform.

## Prerequisites

1. Create a free Sentry account at [sentry.io](https://sentry.io)
2. Create two projects in Sentry:
   - **Backend**: Python/Django project
   - **Frontend**: Next.js project

## Backend Setup

### 1. Install Sentry SDK

```bash
pip install sentry-sdk
```

### 2. Configure Environment Variables

Add to your `.env.production` or backend environment:

```bash
# Sentry Configuration
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production  # or staging, development
SENTRY_RELEASE=uganda-electronics@1.0.0
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of transactions
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% profiling
```

### 3. Initialize Sentry in Django Settings

Add to your `saleor/settings.py`:

```python
# At the top of the file
from uganda_backend_code.sentry_config import init_sentry

# After other configurations
init_sentry()
```

### 4. Test Sentry Integration

```python
# In Django shell
from sentry_sdk import capture_message
capture_message("Test message from Uganda Electronics")
```

Check your Sentry dashboard for the test message.

## Frontend Setup

### 1. Install Sentry SDK

```bash
cd storefront-uganda
pnpm add @sentry/nextjs
```

### 2. Configure Environment Variables

Add to `.env.local` (development) and `.env.production`:

```bash
# Sentry Configuration (Frontend)
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-dsn@sentry.io/frontend-project-id
NEXT_PUBLIC_SENTRY_ENVIRONMENT=production
NEXT_PUBLIC_SENTRY_RELEASE=storefront@1.0.0
NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE=0.1
NEXT_PUBLIC_SENTRY_REPLAY_SESSION_SAMPLE_RATE=0.1
NEXT_PUBLIC_SENTRY_REPLAY_ERROR_SAMPLE_RATE=1.0
```

### 3. Initialize Sentry in Next.js

Create `sentry.client.config.ts` in the root of your Next.js project:

```typescript
import { initSentry } from './src/lib/sentry';

initSentry();
```

Create `sentry.server.config.ts`:

```typescript
import { initSentry } from './src/lib/sentry';

initSentry();
```

Create `sentry.edge.config.ts`:

```typescript
import { initSentry } from './src/lib/sentry';

initSentry();
```

### 4. Update next.config.js

Add Sentry webpack plugin configuration:

```javascript
const { withSentryConfig } = require('@sentry/nextjs');

const nextConfig = {
  // Your existing Next.js config
};

module.exports = withSentryConfig(
  nextConfig,
  {
    silent: true,
    org: 'your-org-name',
    project: 'storefront-uganda',
  },
  {
    widenClientFileUpload: true,
    transpileClientSDK: true,
    tunnelRoute: '/monitoring',
    hideSourceMaps: true,
    disableLogger: true,
  }
);
```

## Usage Examples

### Backend: Capture Payment Errors

```python
from uganda_backend_code.sentry_config import capture_payment_error

try:
    result = mtn_api.request_to_pay(...)
except Exception as e:
    capture_payment_error(
        provider='mtn_momo',
        error_message=str(e),
        context={
            'amount': amount,
            'phone_number_hash': hash_phone(phone),
        }
    )
    raise
```

### Backend: Capture SMS Errors

```python
from uganda_backend_code.sentry_config import capture_sms_error

try:
    sms_service.send_sms(phone, message)
except Exception as e:
    capture_sms_error(
        recipient=phone,
        error_message=str(e),
        context={
            'message_type': 'order_confirmation',
        }
    )
```

### Backend: Trace Payment Performance

```python
from uganda_backend_code.sentry_config import trace_payment_transaction

@trace_payment_transaction('mtn_momo')
def process_mtn_payment(order_id, amount, phone):
    # Your payment processing logic
    return result
```

### Frontend: Capture Checkout Errors

```typescript
import { captureCheckoutError } from '@/lib/sentry';

try {
  await createCheckout(items);
} catch (error) {
  captureCheckoutError(error as Error, {
    itemCount: items.length,
    totalAmount: total,
  });
  throw error;
}
```

### Frontend: Capture Payment Errors

```typescript
import { capturePaymentError } from '@/lib/sentry';

try {
  await initiatePayment(provider, phone, amount);
} catch (error) {
  capturePaymentError(provider, error as Error, {
    amount,
    phoneHash: hashPhone(phone),
  });
}
```

### Frontend: Track Page Performance

```typescript
import { trackPagePerformance } from '@/lib/sentry';

export default function CheckoutPage() {
  useEffect(() => {
    const tracker = trackPagePerformance('Checkout Page');
    return () => tracker.finish();
  }, []);

  return <div>...</div>;
}
```

## Sentry Features Enabled

### Backend

✅ **Error Tracking**: All unhandled exceptions
✅ **Performance Monitoring**: API endpoints, database queries
✅ **Celery Integration**: Background task monitoring
✅ **Redis Integration**: Cache performance
✅ **Custom Context**: Payment, SMS, order-specific data
✅ **Data Scrubbing**: Automatic PII removal
✅ **Source Maps**: Code context for errors

### Frontend

✅ **Error Tracking**: JavaScript exceptions
✅ **Performance Monitoring**: Page loads, API calls
✅ **Session Replay**: Video-like reproduction of user sessions
✅ **GraphQL Integration**: Query/mutation error tracking
✅ **Custom Context**: Checkout, payment context
✅ **User Privacy**: PII filtering and hashing
✅ **Source Maps**: Original source code in errors

## Alerts & Notifications

### Recommended Alert Rules

1. **High Error Rate**
   - Condition: Error rate > 10 per minute
   - Action: Notify #tech-alerts Slack channel

2. **Payment Failures**
   - Condition: payment_provider tag exists + error
   - Action: Notify #payments Slack channel + Email

3. **API Performance Degradation**
   - Condition: p95 response time > 2 seconds
   - Action: Notify #tech-alerts

4. **SMS Delivery Failures**
   - Condition: sms_error tag + count > 5 in 10 minutes
   - Action: Notify #operations

### Setting up Alerts

1. Go to Sentry Project Settings > Alerts
2. Click "Create Alert Rule"
3. Choose conditions and actions
4. Set up integrations (Slack, Email, PagerDuty)

## Monitoring Dashboards

### Key Metrics to Track

**Backend:**
- Payment success rate by provider
- Average payment processing time
- SMS delivery rate
- API error rate
- Celery task success rate

**Frontend:**
- Checkout completion rate
- Page load performance
- GraphQL error rate
- User session quality

### Creating Custom Dashboards

1. Go to Dashboards in Sentry
2. Create new dashboard: "Uganda Electronics - Production"
3. Add widgets:
   - Error rate over time
   - Payment errors by provider
   - Top 10 errors
   - Performance metrics
   - User sessions

## Privacy & Compliance

### PII Handling

The configuration automatically:
- ✅ Filters authentication tokens
- ✅ Hashes email addresses
- ✅ Hashes phone numbers
- ✅ Removes credit card data
- ✅ Filters API keys and secrets

### GDPR Compliance

To remove user data from Sentry:

```bash
# Using Sentry CLI
sentry-cli data-purge --project uganda-electronics-backend --user-id <hashed-id>
```

## Troubleshooting

### Sentry not capturing errors

1. Check DSN is correct
2. Verify environment variables are loaded
3. Check network connectivity to sentry.io
4. Review beforeSend filters (might be filtering too much)

### Too many errors

1. Review ignoreErrors configuration
2. Adjust sample rates
3. Add more specific filters in beforeSend

### Missing source maps

**Backend:**
```bash
# Ensure debug symbols are included
pip install sentry-sdk[django]
```

**Frontend:**
```bash
# Upload source maps
npx @sentry/wizard@latest -i nextjs
```

### Performance overhead

- Reduce traces_sample_rate (default 0.1 = 10%)
- Reduce profiles_sample_rate
- Disable session replay for low-value pages

## Cost Optimization

Sentry pricing is based on:
- Events (errors)
- Transactions (performance monitoring)
- Replays (session recordings)

### Free Tier Limits
- 5,000 errors/month
- 10,000 performance units/month
- 50 replays/month

### Staying Within Free Tier

1. Set appropriate sample rates (10% recommended)
2. Filter out known/expected errors
3. Use beforeSend to drop low-priority errors
4. Monitor quota usage in Sentry dashboard

### Quota Management

```python
# Backend: Drop low-priority errors in production
def before_send_filter(event, hint):
    if event.get('level') == 'warning':
        return None  # Don't send warnings to Sentry
    return event
```

## Support

- Sentry Documentation: https://docs.sentry.io
- Community Forum: https://forum.sentry.io
- Status Page: https://status.sentry.io

## Next Steps

1. ✅ Create Sentry account
2. ✅ Install SDKs (backend + frontend)
3. ✅ Configure environment variables
4. ✅ Test error capture
5. ⏳ Set up alert rules
6. ⏳ Create monitoring dashboards
7. ⏳ Integrate with Slack/Email
8. ⏳ Train team on Sentry usage
