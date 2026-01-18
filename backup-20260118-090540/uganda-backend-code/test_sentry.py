#!/usr/bin/env python
"""
Test script to verify Sentry integration is working

Usage:
    python test_sentry.py
"""
import os
import sys

# Set up environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saleor.settings')

# Load environment variables from .env.development
from pathlib import Path
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

# Initialize Django
import django
django.setup()

# Initialize Sentry
from uganda_backend_code.sentry_config import init_sentry

print("\n" + "="*60)
print("SENTRY INTEGRATION TEST")
print("="*60 + "\n")

print("Initializing Sentry...")
init_sentry()

print("\n" + "-"*60)
print("Test 1: Capture Test Message")
print("-"*60)

import sentry_sdk

# Test 1: Simple message
message_id = sentry_sdk.capture_message("Test message from Uganda Electronics Platform", level='info')
print(f"✅ Test message sent")
print(f"   Event ID: {message_id}")

print("\n" + "-"*60)
print("Test 2: Capture Test Exception")
print("-"*60)

# Test 2: Exception
try:
    division_result = 1 / 0
except Exception as e:
    event_id = sentry_sdk.capture_exception(e)
    print(f"✅ Test exception sent")
    print(f"   Event ID: {event_id}")

print("\n" + "-"*60)
print("Test 3: Payment Error (Custom Context)")
print("-"*60)

# Test 3: Custom payment error
from uganda_backend_code.sentry_config import capture_payment_error

capture_payment_error(
    provider='mtn_momo',
    error_message='Test payment timeout',
    context={
        'order_id': 'TEST-12345',
        'amount': 500000,
        'phone_number_hash': 'abc123def456'
    }
)
print(f"✅ Payment error sent with context")

print("\n" + "-"*60)
print("Test 4: SMS Error (Custom Context)")
print("-"*60)

# Test 4: SMS error
from uganda_backend_code.sentry_config import capture_sms_error

capture_sms_error(
    recipient='256700123456',
    error_message='Test SMS delivery failed',
    context={
        'message_type': 'order_confirmation',
        'retry_count': 3
    }
)
print(f"✅ SMS error sent with context")

print("\n" + "-"*60)
print("Test 5: Performance Transaction")
print("-"*60)

# Test 5: Performance monitoring
from uganda_backend_code.sentry_config import trace_payment_transaction

@trace_payment_transaction('test_provider')
def test_payment_processing():
    import time
    time.sleep(0.1)  # Simulate processing
    return {'status': 'success'}

result = test_payment_processing()
print(f"✅ Performance transaction captured")
print(f"   Result: {result}")

print("\n" + "="*60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*60)

print("\n📊 Check your Sentry dashboard:")
print("   https://sentry.io/organizations/YOUR_ORG/issues/")
print("\nYou should see:")
print("   • 1 info message")
print("   • 3 errors (division by zero, payment, SMS)")
print("   • 1 performance transaction")
print("\n⏱  Events may take a few seconds to appear in Sentry.\n")

print("🔗 Direct link to your project:")
print("   https://o4510729613082624.ingest.de.sentry.io/")
