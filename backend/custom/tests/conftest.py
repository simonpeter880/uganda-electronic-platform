"""
Pytest configuration and fixtures for Uganda Electronics Platform tests
"""
import os
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Django setup for pytest
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saleor.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from graphene.test import Client as GrapheneClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Django test client for API requests"""
    return Client()


@pytest.fixture
def graphql_client():
    """GraphQL test client"""
    from saleor.graphql.schema import schema
    return GrapheneClient(schema)


@pytest.fixture
def admin_user(db):
    """Create admin user for testing"""
    return User.objects.create_superuser(
        email='admin@test.com',
        password='testpass123',
        is_staff=True,
        is_active=True
    )


@pytest.fixture
def customer_user(db):
    """Create regular customer user"""
    return User.objects.create_user(
        email='customer@test.com',
        password='testpass123',
        is_staff=False,
        is_active=True
    )


@pytest.fixture
def uganda_district(db):
    """Create a test Uganda district"""
    from uganda_backend_code.models.uganda_models import UgandaDistrict

    return UgandaDistrict.objects.create(
        name='Kampala',
        region='Central',
        delivery_available=True,
        delivery_fee=Decimal('10000.00'),
        estimated_delivery_days=2,
        sub_areas=['Nakasero', 'Kololo', 'Ntinda'],
        is_active=True
    )


@pytest.fixture
def test_order(db, customer_user):
    """Create a test order"""
    from saleor.order.models import Order

    order = Order.objects.create(
        user=customer_user,
        status='unfulfilled',
        total_gross_amount=Decimal('500000.00'),
        currency='UGX',
        billing_address=None,
        shipping_address=None
    )
    return order


@pytest.fixture
def mobile_money_transaction(db, test_order):
    """Create a test mobile money transaction"""
    from uganda_backend_code.models.uganda_models import MobileMoneyTransaction

    return MobileMoneyTransaction.objects.create(
        order=test_order,
        provider='mtn_momo',
        phone_number='256700123456',
        transaction_reference='MTN_TEST_12345',
        amount=Decimal('500000.00'),
        currency='UGX',
        status='pending',
        payment_method='mobile_money',
        provider_response={}
    )


@pytest.fixture
def order_delivery(db, test_order, uganda_district):
    """Create a test order delivery"""
    from uganda_backend_code.models.uganda_models import OrderDeliveryUganda

    return OrderDeliveryUganda.objects.create(
        order=test_order,
        district=uganda_district,
        recipient_name='John Doe',
        recipient_phone='256700123456',
        landmark='Near City Square',
        delivery_method='home_delivery',
        status='pending'
    )


@pytest.fixture
def mock_mtn_api():
    """Mock MTN Mobile Money API responses"""
    with patch('uganda_backend_code.services.mobile_money.MTNMoMoAPI') as mock:
        # Mock access token
        mock.return_value.get_access_token.return_value = 'mock_access_token_12345'

        # Mock request to pay
        mock.return_value.request_to_pay.return_value = {
            'status': 'success',
            'transaction_id': 'MTN_TEST_12345',
            'message': 'Payment initiated successfully'
        }

        # Mock transaction status
        mock.return_value.check_transaction_status.return_value = {
            'status': 'SUCCESSFUL',
            'amount': '500000',
            'currency': 'UGX',
            'financialTransactionId': '123456789',
            'externalId': 'order_123',
            'payer': {
                'partyIdType': 'MSISDN',
                'partyId': '256700123456'
            }
        }

        yield mock


@pytest.fixture
def mock_airtel_api():
    """Mock Airtel Money API responses"""
    with patch('uganda_backend_code.services.mobile_money.AirtelMoneyAPI') as mock:
        # Mock access token
        mock.return_value.get_access_token.return_value = 'mock_airtel_token'

        # Mock initiate payment
        mock.return_value.initiate_payment.return_value = {
            'status': 'success',
            'transaction_id': 'AIRTEL_TEST_12345',
            'message': 'Payment initiated'
        }

        # Mock transaction status
        mock.return_value.get_transaction_status.return_value = {
            'status': 'TS',  # Transaction Successful
            'data': {
                'transaction': {
                    'id': 'AIRTEL_TEST_12345',
                    'status': 'TS',
                    'message': 'Success'
                }
            }
        }

        yield mock


@pytest.fixture
def mock_sms_api():
    """Mock Africa's Talking SMS API"""
    with patch('uganda_backend_code.services.sms_service.AfricasTalkingAPI') as mock:
        mock.return_value.send_sms.return_value = {
            'SMSMessageData': {
                'Message': 'Sent to 1/1 Total Cost: UGX 30',
                'Recipients': [{
                    'statusCode': 101,
                    'number': '256700123456',
                    'status': 'Success',
                    'cost': 'UGX 30',
                    'messageId': 'ATXid_mock123'
                }]
            }
        }

        yield mock


@pytest.fixture
def auth_token(admin_user):
    """Generate JWT token for authenticated requests"""
    from saleor.graphql.core.utils import generate_token
    return generate_token(admin_user)


@pytest.fixture
def graphql_headers(auth_token):
    """Headers for authenticated GraphQL requests"""
    return {
        'HTTP_AUTHORIZATION': f'Bearer {auth_token}',
        'CONTENT_TYPE': 'application/json'
    }
