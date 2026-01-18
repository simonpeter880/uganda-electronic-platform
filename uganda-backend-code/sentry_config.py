"""
Sentry configuration for Uganda Electronics Platform
"""
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry():
    """
    Initialize Sentry for error tracking and performance monitoring

    Environment variables required:
    - SENTRY_DSN: Your Sentry project DSN
    - SENTRY_ENVIRONMENT: Environment name (production, staging, development)
    - SENTRY_RELEASE: Release version (optional, defaults to git commit hash)
    """
    sentry_dsn = os.environ.get('SENTRY_DSN')

    if not sentry_dsn:
        print("⚠️  Sentry DSN not configured. Error tracking disabled.")
        return

    environment = os.environ.get('SENTRY_ENVIRONMENT', 'development')
    release = os.environ.get('SENTRY_RELEASE', None)

    # If release not set, try to get git commit hash
    if not release:
        try:
            import subprocess
            release = subprocess.check_output(
                ['git', 'rev-parse', '--short', 'HEAD']
            ).decode('utf-8').strip()
            release = f'uganda-electronics@{release}'
        except Exception:
            release = 'uganda-electronics@unknown'

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=release,

        # Integrations
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
            RedisIntegration(),
            LoggingIntegration(
                level=None,  # Capture records from all log levels
                event_level='ERROR'  # Send events for ERROR and above
            ),
        ],

        # Performance Monitoring
        traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),

        # Profiling
        profiles_sample_rate=float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),

        # Error Sampling
        sample_rate=1.0,  # Send all errors

        # Data Scrubbing - Remove sensitive data
        send_default_pii=False,

        # Request body size
        max_request_body_size='medium',

        # Breadcrumbs
        max_breadcrumbs=50,

        # Before send hook to filter events
        before_send=before_send_filter,

        # Before breadcrumb hook
        before_breadcrumb=before_breadcrumb_filter,
    )

    print(f"✅ Sentry initialized (env: {environment}, release: {release})")


def before_send_filter(event, hint):
    """
    Filter and modify events before sending to Sentry

    - Remove sensitive data
    - Add custom context
    - Filter unwanted errors
    """
    # Ignore specific errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']

        # Ignore common errors that aren't actionable
        ignored_exceptions = [
            'DisconnectedError',
            'ConnectionResetError',
            'BrokenPipeError',
        ]

        if exc_type.__name__ in ignored_exceptions:
            return None

    # Remove sensitive data from request
    if 'request' in event:
        request = event['request']

        # Remove headers with sensitive info
        if 'headers' in request:
            sensitive_headers = [
                'Authorization',
                'X-Api-Key',
                'Cookie',
                'X-CSRF-Token'
            ]
            for header in sensitive_headers:
                if header in request['headers']:
                    request['headers'][header] = '[Filtered]'

        # Remove sensitive query params
        if 'query_string' in request:
            request['query_string'] = '[Filtered]'

        # Remove sensitive POST data
        if 'data' in request:
            sensitive_fields = [
                'password',
                'api_key',
                'token',
                'secret',
                'credit_card'
            ]
            for field in sensitive_fields:
                if field in request['data']:
                    request['data'][field] = '[Filtered]'

    # Add custom context
    event['tags'] = event.get('tags', {})
    event['tags']['platform'] = 'uganda-electronics'

    # Add user context if available (without PII)
    if 'user' in event and event['user'].get('email'):
        # Hash email for privacy
        import hashlib
        email = event['user']['email']
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:16]
        event['user']['id'] = email_hash
        event['user']['email'] = None  # Remove actual email

    return event


def before_breadcrumb_filter(crumb, hint):
    """
    Filter breadcrumbs before adding to event
    """
    # Remove sensitive data from query breadcrumbs
    if crumb.get('category') == 'query':
        if 'data' in crumb:
            crumb['data'] = '[SQL Query]'

    # Remove sensitive HTTP request data
    if crumb.get('category') == 'http':
        if 'data' in crumb and isinstance(crumb['data'], dict):
            # Remove authorization headers
            if 'headers' in crumb['data']:
                crumb['data']['headers'].pop('Authorization', None)

    return crumb


def capture_payment_error(provider, error_message, context=None):
    """
    Capture payment-specific errors with structured data

    Args:
        provider: Payment provider (mtn_momo, airtel_money)
        error_message: Error message
        context: Additional context dict
    """
    with sentry_sdk.push_scope() as scope:
        scope.set_tag('payment_provider', provider)
        scope.set_context('payment_error', {
            'provider': provider,
            'message': error_message,
            **(context or {})
        })
        sentry_sdk.capture_message(
            f'Payment Error: {provider} - {error_message}',
            level='error'
        )


def capture_sms_error(recipient, error_message, context=None):
    """
    Capture SMS-specific errors

    Args:
        recipient: Phone number (will be hashed)
        error_message: Error message
        context: Additional context dict
    """
    import hashlib
    recipient_hash = hashlib.sha256(recipient.encode()).hexdigest()[:16]

    with sentry_sdk.push_scope() as scope:
        scope.set_tag('sms_error', True)
        scope.set_context('sms_error', {
            'recipient_hash': recipient_hash,
            'message': error_message,
            **(context or {})
        })
        sentry_sdk.capture_message(
            f'SMS Error: {error_message}',
            level='error'
        )


def capture_order_error(order_id, error_message, context=None):
    """
    Capture order-specific errors

    Args:
        order_id: Order ID or number
        error_message: Error message
        context: Additional context dict
    """
    with sentry_sdk.push_scope() as scope:
        scope.set_tag('order_error', True)
        scope.set_context('order', {
            'order_id': str(order_id),
            'message': error_message,
            **(context or {})
        })
        sentry_sdk.capture_message(
            f'Order Error: {order_id} - {error_message}',
            level='error'
        )


# Performance monitoring helpers
def trace_payment_transaction(provider):
    """
    Decorator to trace payment transactions

    Usage:
        @trace_payment_transaction('mtn_momo')
        def process_payment(...):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with sentry_sdk.start_transaction(
                op='payment.process',
                name=f'{provider}.{func.__name__}'
            ) as transaction:
                transaction.set_tag('payment_provider', provider)
                try:
                    result = func(*args, **kwargs)
                    transaction.set_status('ok')
                    return result
                except Exception as e:
                    transaction.set_status('error')
                    raise
        return wrapper
    return decorator


def trace_sms_delivery():
    """
    Decorator to trace SMS delivery
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with sentry_sdk.start_transaction(
                op='sms.send',
                name=f'sms.{func.__name__}'
            ) as transaction:
                try:
                    result = func(*args, **kwargs)
                    transaction.set_status('ok')
                    return result
                except Exception as e:
                    transaction.set_status('error')
                    raise
        return wrapper
    return decorator
