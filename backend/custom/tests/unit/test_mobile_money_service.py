"""
Unit tests for mobile money services
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from uganda_backend_code.services.mobile_money import (
    MobileMoneyService,
    MTNMoMoAPI,
    AirtelMoneyAPI,
    MobileMoneyError
)


class TestMobileMoneyService:
    """Test MobileMoneyService class"""

    def test_validate_phone_number_valid(self):
        """Test phone number validation with valid numbers"""
        service = MobileMoneyService()

        valid_numbers = [
            '256700123456',
            '256750987654',
            '256780111222'
        ]

        for number in valid_numbers:
            assert service.validate_phone_number(number) is True

    def test_validate_phone_number_invalid(self):
        """Test phone number validation with invalid numbers"""
        service = MobileMoneyService()

        invalid_numbers = [
            '123456',
            '256',
            '25670012345',  # Too short
            '2567001234567',  # Too long
            '257700123456',  # Wrong country code
            'invalid',
            ''
        ]

        for number in invalid_numbers:
            assert service.validate_phone_number(number) is False

    def test_validate_amount_valid(self):
        """Test amount validation with valid amounts"""
        service = MobileMoneyService()

        valid_amounts = [
            Decimal('100'),
            Decimal('1000.00'),
            Decimal('500000'),
            Decimal('999999.99')
        ]

        for amount in valid_amounts:
            assert service.validate_amount(amount) is True

    def test_validate_amount_invalid(self):
        """Test amount validation with invalid amounts"""
        service = MobileMoneyService()

        invalid_amounts = [
            Decimal('0'),
            Decimal('-100'),
            Decimal('50'),  # Below minimum
        ]

        for amount in invalid_amounts:
            assert service.validate_amount(amount) is False

    @patch('uganda_backend_code.services.mobile_money.MTNMoMoAPI')
    def test_initiate_mtn_payment(self, mock_mtn_class):
        """Test initiating MTN payment"""
        service = MobileMoneyService()

        # Setup mock
        mock_mtn = Mock()
        mock_mtn.get_access_token.return_value = 'mock_token'
        mock_mtn.request_to_pay.return_value = {
            'transaction_id': 'MTN_123',
            'status': 'pending'
        }
        mock_mtn_class.return_value = mock_mtn

        result = service.initiate_payment(
            provider='mtn_momo',
            phone_number='256700123456',
            amount=Decimal('10000'),
            external_id='order_123'
        )

        assert result['transaction_id'] == 'MTN_123'
        assert result['status'] == 'pending'
        mock_mtn.request_to_pay.assert_called_once()

    @patch('uganda_backend_code.services.mobile_money.AirtelMoneyAPI')
    def test_initiate_airtel_payment(self, mock_airtel_class):
        """Test initiating Airtel payment"""
        service = MobileMoneyService()

        # Setup mock
        mock_airtel = Mock()
        mock_airtel.get_access_token.return_value = 'mock_token'
        mock_airtel.initiate_payment.return_value = {
            'transaction_id': 'AIRTEL_123',
            'status': 'pending'
        }
        mock_airtel_class.return_value = mock_airtel

        result = service.initiate_payment(
            provider='airtel_money',
            phone_number='256750123456',
            amount=Decimal('10000'),
            external_id='order_123'
        )

        assert result['transaction_id'] == 'AIRTEL_123'
        mock_airtel.initiate_payment.assert_called_once()

    def test_initiate_payment_invalid_provider(self):
        """Test payment initiation with invalid provider"""
        service = MobileMoneyService()

        with pytest.raises(MobileMoneyError) as exc_info:
            service.initiate_payment(
                provider='invalid_provider',
                phone_number='256700123456',
                amount=Decimal('10000'),
                external_id='order_123'
            )

        assert 'Invalid provider' in str(exc_info.value)

    def test_initiate_payment_invalid_phone(self):
        """Test payment initiation with invalid phone"""
        service = MobileMoneyService()

        with pytest.raises(MobileMoneyError) as exc_info:
            service.initiate_payment(
                provider='mtn_momo',
                phone_number='invalid',
                amount=Decimal('10000'),
                external_id='order_123'
            )

        assert 'Invalid phone number' in str(exc_info.value)

    def test_initiate_payment_invalid_amount(self):
        """Test payment initiation with invalid amount"""
        service = MobileMoneyService()

        with pytest.raises(MobileMoneyError) as exc_info:
            service.initiate_payment(
                provider='mtn_momo',
                phone_number='256700123456',
                amount=Decimal('0'),
                external_id='order_123'
            )

        assert 'Invalid amount' in str(exc_info.value)


class TestMTNMoMoAPI:
    """Test MTN Mobile Money API client"""

    @patch('uganda_backend_code.services.mobile_money.RetryingSession')
    def test_get_access_token(self, mock_session):
        """Test getting MTN access token"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'mock_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600
        }

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        api = MTNMoMoAPI(
            api_url='https://test.api',
            api_user='user',
            api_key='key',
            subscription_key='sub_key'
        )

        token = api.get_access_token()
        assert token == 'mock_access_token'

    @patch('uganda_backend_code.services.mobile_money.RetryingSession')
    @patch('uganda_backend_code.services.mobile_money.cache')
    def test_token_caching(self, mock_cache, mock_session):
        """Test that tokens are cached"""
        mock_cache.get.return_value = 'cached_token'

        api = MTNMoMoAPI(
            api_url='https://test.api',
            api_user='user',
            api_key='key',
            subscription_key='sub_key'
        )

        token = api.get_access_token()
        assert token == 'cached_token'
        mock_session.assert_not_called()

    @patch('uganda_backend_code.services.mobile_money.RetryingSession')
    def test_request_to_pay(self, mock_session):
        """Test MTN request to pay"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {'X-Reference-Id': 'ref_123'}

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        api = MTNMoMoAPI(
            api_url='https://test.api',
            api_user='user',
            api_key='key',
            subscription_key='sub_key'
        )

        with patch.object(api, 'get_access_token', return_value='token'):
            result = api.request_to_pay(
                phone_number='256700123456',
                amount=Decimal('10000'),
                external_id='order_123',
                payer_message='Test payment'
            )

        assert result['reference_id'] == 'ref_123'
        assert result['status'] == 'pending'


class TestAirtelMoneyAPI:
    """Test Airtel Money API client"""

    @patch('uganda_backend_code.services.mobile_money.RetryingSession')
    def test_get_access_token(self, mock_session):
        """Test getting Airtel access token"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'access_token': 'airtel_token',
                'expires_in': '3600'
            }
        }

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        api = AirtelMoneyAPI(
            api_url='https://test.api',
            client_id='client',
            client_secret='secret'
        )

        token = api.get_access_token()
        assert token == 'airtel_token'

    @patch('uganda_backend_code.services.mobile_money.RetryingSession')
    def test_initiate_payment(self, mock_session):
        """Test Airtel initiate payment"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'transaction': {
                    'id': 'airtel_123',
                    'status': 'TIP'  # Transaction in progress
                }
            },
            'status': {
                'code': '200',
                'message': 'Success'
            }
        }

        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        api = AirtelMoneyAPI(
            api_url='https://test.api',
            client_id='client',
            client_secret='secret'
        )

        with patch.object(api, 'get_access_token', return_value='token'):
            result = api.initiate_payment(
                phone_number='256750123456',
                amount=Decimal('10000'),
                reference='order_123'
            )

        assert result['transaction_id'] == 'airtel_123'
