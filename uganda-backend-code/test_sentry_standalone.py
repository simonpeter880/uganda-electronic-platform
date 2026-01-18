#!/usr/bin/env python
"""
Standalone Sentry Test (No Django Required)
Tests Sentry integration without Django dependencies

Usage:
    python test_sentry_standalone.py
"""
import os
import sys
from pathlib import Path

# Load environment variables from .env.development
env_file = Path(__file__).parent.parent / '.env.development'

if env_file.exists():
    print(f"✅ Loading environment from: {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)
else:
    print(f"⚠️  Environment file not found: {env_file}")

# Get Sentry DSN
SENTRY_DSN = os.environ.get('SENTRY_DSN')

if not SENTRY_DSN:
    print("❌ Error: SENTRY_DSN not found in environment!")
    print("Please set SENTRY_DSN in .env.development")
    sys.exit(1)

print("\n" + "="*60)
print("SENTRY STANDALONE TEST")
print("="*60 + "\n")

print(f"Sentry DSN: {SENTRY_DSN[:50]}...")
print(f"Environment: {os.environ.get('SENTRY_ENVIRONMENT', 'not set')}")
print(f"Release: {os.environ.get('SENTRY_RELEASE', 'not set')}")

print("\nInitializing Sentry...")

import sentry_sdk

sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=os.environ.get('SENTRY_ENVIRONMENT', 'development'),
    release=os.environ.get('SENTRY_RELEASE', 'uganda-electronics@dev'),
    traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
    send_default_pii=False,
)

print("✅ Sentry initialized successfully!")

print("\n" + "-"*60)
print("Test 1: Capture Info Message")
print("-"*60)

message_id = sentry_sdk.capture_message(
    "Test message from Uganda Electronics Platform",
    level='info'
)
print(f"✅ Test message sent")
print(f"   Event ID: {message_id}")

print("\n" + "-"*60)
print("Test 2: Capture Exception")
print("-"*60)

try:
    division_result = 1 / 0
except Exception as e:
    event_id = sentry_sdk.capture_exception(e)
    print(f"✅ Test exception sent")
    print(f"   Event ID: {event_id}")
    print(f"   Exception: {type(e).__name__}: {e}")

print("\n" + "-"*60)
print("Test 3: Custom Context - Payment Error")
print("-"*60)

with sentry_sdk.push_scope() as scope:
    scope.set_tag('payment_provider', 'mtn_momo')
    scope.set_tag('error_type', 'payment')
    scope.set_context('payment_error', {
        'provider': 'mtn_momo',
        'order_id': 'TEST-12345',
        'amount': 500000,
        'phone_hash': 'abc123def456',
        'error_message': 'Test payment timeout'
    })
    event_id = sentry_sdk.capture_message(
        'Payment Error: mtn_momo - Test payment timeout',
        level='error'
    )
    print(f"✅ Payment error sent")
    print(f"   Event ID: {event_id}")

print("\n" + "-"*60)
print("Test 4: Custom Context - SMS Error")
print("-"*60)

with sentry_sdk.push_scope() as scope:
    scope.set_tag('sms_error', True)
    scope.set_context('sms_error', {
        'recipient_hash': '1a2b3c4d5e6f',
        'message_type': 'order_confirmation',
        'retry_count': 3,
        'error_message': 'Test SMS delivery failed'
    })
    event_id = sentry_sdk.capture_message(
        'SMS Error: Test SMS delivery failed',
        level='error'
    )
    print(f"✅ SMS error sent")
    print(f"   Event ID: {event_id}")

print("\n" + "-"*60)
print("Test 5: Performance Transaction")
print("-"*60)

import time

with sentry_sdk.start_transaction(
    op='payment.process',
    name='test_provider.test_payment'
) as transaction:
    transaction.set_tag('payment_provider', 'test_provider')

    # Simulate processing
    time.sleep(0.1)

    transaction.set_status('ok')
    print(f"✅ Performance transaction captured")
    print(f"   Transaction: {transaction.name}")

print("\n" + "-"*60)
print("Test 6: Custom Error with Breadcrumbs")
print("-"*60)

sentry_sdk.add_breadcrumb(
    category='order',
    message='Order created',
    level='info',
    data={'order_id': 'TEST-12345', 'amount': 500000}
)

sentry_sdk.add_breadcrumb(
    category='payment',
    message='Payment initiated',
    level='info',
    data={'provider': 'mtn_momo', 'phone': '256700******'}
)

sentry_sdk.add_breadcrumb(
    category='payment',
    message='Payment failed',
    level='error',
    data={'error': 'timeout'}
)

try:
    raise ValueError("Simulated payment processing error")
except Exception as e:
    event_id = sentry_sdk.capture_exception(e)
    print(f"✅ Error with breadcrumbs sent")
    print(f"   Event ID: {event_id}")
    print(f"   Breadcrumbs: 3 added (order, payment x2)")

# Flush events (make sure they're sent before script exits)
print("\n" + "-"*60)
print("Flushing events to Sentry...")
print("-"*60)

client = sentry_sdk.Hub.current.client
if client:
    client.flush(timeout=5)
    print("✅ Events flushed")

print("\n" + "="*60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*60)

print("\n📊 Check your Sentry dashboard:")
print("   https://sentry.io/")
print("\nYou should see:")
print("   • 1 info message")
print("   • 4 errors (division, payment, SMS, ValueError)")
print("   • 1 performance transaction")
print("   • Custom contexts and tags")
print("   • Breadcrumbs on the last error")
print("\n⏱  Events may take 5-10 seconds to appear in Sentry.")

print("\n🔗 Your project:")
print("   Region: Germany (de.sentry.io)")
print(f"   DSN: {SENTRY_DSN[:50]}...")

print("\n✅ Test complete! Check your dashboard now.")
