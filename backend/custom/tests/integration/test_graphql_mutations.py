"""
Integration tests for Uganda GraphQL mutations
"""
import pytest
from decimal import Decimal
from graphql_relay import to_global_id
from unittest.mock import patch


@pytest.mark.django_db
class TestMobileMoneyMutations:
    """Test mobile money payment mutations"""

    def test_initiate_mtn_payment(self, graphql_client, test_order, mock_mtn_api):
        """Test initiating MTN Mobile Money payment"""
        order_id = to_global_id('Order', test_order.id)

        mutation = f"""
            mutation {{
                initiateMobileMoneyPayment(input: {{
                    orderId: "{order_id}"
                    phoneNumber: "256700123456"
                    provider: "mtn_momo"
                }}) {{
                    transactionId
                    status
                    message
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert 'errors' not in result

        payment = result['data']['initiateMobileMoneyPayment']
        assert payment['status'] == 'pending'
        assert payment['transactionId'] is not None
        assert len(payment['errors']) == 0

    def test_initiate_airtel_payment(self, graphql_client, test_order, mock_airtel_api):
        """Test initiating Airtel Money payment"""
        order_id = to_global_id('Order', test_order.id)

        mutation = f"""
            mutation {{
                initiateMobileMoneyPayment(input: {{
                    orderId: "{order_id}"
                    phoneNumber: "256750123456"
                    provider: "airtel_money"
                }}) {{
                    transactionId
                    status
                    message
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert 'errors' not in result

        payment = result['data']['initiateMobileMoneyPayment']
        assert payment['status'] in ['pending', 'processing']

    def test_invalid_phone_number(self, graphql_client, test_order):
        """Test payment with invalid phone number"""
        order_id = to_global_id('Order', test_order.id)

        mutation = f"""
            mutation {{
                initiateMobileMoneyPayment(input: {{
                    orderId: "{order_id}"
                    phoneNumber: "123456"
                    provider: "mtn_momo"
                }}) {{
                    transactionId
                    status
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        payment = result['data']['initiateMobileMoneyPayment']

        assert len(payment['errors']) > 0
        assert any('phone' in error['field'].lower() for error in payment['errors'])

    def test_check_payment_status(self, graphql_client, mobile_money_transaction, mock_mtn_api):
        """Test checking payment status"""
        txn_id = to_global_id('MobileMoneyTransaction', mobile_money_transaction.id)

        mutation = f"""
            mutation {{
                checkMobileMoneyPaymentStatus(input: {{
                    transactionId: "{txn_id}"
                }}) {{
                    status
                    transactionReference
                    message
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert 'errors' not in result

        status = result['data']['checkMobileMoneyPaymentStatus']
        assert status['status'] in ['pending', 'successful', 'failed']

    def test_payment_with_zero_amount(self, graphql_client, test_order):
        """Test payment validation with zero amount"""
        # Set order amount to zero
        test_order.total_gross_amount = Decimal('0.00')
        test_order.save()

        order_id = to_global_id('Order', test_order.id)

        mutation = f"""
            mutation {{
                initiateMobileMoneyPayment(input: {{
                    orderId: "{order_id}"
                    phoneNumber: "256700123456"
                    provider: "mtn_momo"
                }}) {{
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        payment = result['data']['initiateMobileMoneyPayment']

        assert len(payment['errors']) > 0


@pytest.mark.django_db
class TestOrderDeliveryMutations:
    """Test order delivery mutations"""

    def test_create_order_delivery(self, graphql_client, test_order, uganda_district):
        """Test creating order delivery"""
        order_id = to_global_id('Order', test_order.id)
        district_id = to_global_id('UgandaDistrict', uganda_district.id)

        mutation = f"""
            mutation {{
                createOrderDelivery(input: {{
                    orderId: "{order_id}"
                    districtId: "{district_id}"
                    recipientName: "Jane Doe"
                    recipientPhone: "256700987654"
                    landmark: "Near Central Market"
                    deliveryMethod: "home_delivery"
                }}) {{
                    delivery {{
                        id
                        recipientName
                        status
                        district {{
                            name
                        }}
                    }}
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert 'errors' not in result

        delivery = result['data']['createOrderDelivery']['delivery']
        assert delivery['recipientName'] == 'Jane Doe'
        assert delivery['status'] == 'pending'
        assert delivery['district']['name'] == 'Kampala'

    def test_update_delivery_status(self, graphql_client, order_delivery):
        """Test updating delivery status"""
        delivery_id = to_global_id('OrderDeliveryUganda', order_delivery.id)

        mutation = f"""
            mutation {{
                updateDeliveryStatus(input: {{
                    deliveryId: "{delivery_id}"
                    status: "out_for_delivery"
                    deliveryPersonnel: "John Driver"
                }}) {{
                    delivery {{
                        status
                        deliveryPersonnel
                    }}
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert 'errors' not in result

        delivery = result['data']['updateDeliveryStatus']['delivery']
        assert delivery['status'] == 'out_for_delivery'
        assert delivery['deliveryPersonnel'] == 'John Driver'

    def test_invalid_delivery_phone(self, graphql_client, test_order, uganda_district):
        """Test delivery creation with invalid phone"""
        order_id = to_global_id('Order', test_order.id)
        district_id = to_global_id('UgandaDistrict', uganda_district.id)

        mutation = f"""
            mutation {{
                createOrderDelivery(input: {{
                    orderId: "{order_id}"
                    districtId: "{district_id}"
                    recipientName: "Test User"
                    recipientPhone: "invalid"
                    deliveryMethod: "home_delivery"
                }}) {{
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        delivery_result = result['data']['createOrderDelivery']

        assert len(delivery_result['errors']) > 0


@pytest.mark.django_db
class TestInstallmentMutations:
    """Test installment plan mutations"""

    def test_create_installment_plan(self, graphql_client, test_order):
        """Test creating installment plan"""
        order_id = to_global_id('Order', test_order.id)

        mutation = f"""
            mutation {{
                createInstallmentPlan(input: {{
                    orderId: "{order_id}"
                    downPayment: "150000.00"
                    numberOfPayments: 3
                    paymentFrequency: "monthly"
                }}) {{
                    plan {{
                        id
                        downPayment
                        remainingAmount
                        numberOfPayments
                        status
                    }}
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert 'errors' not in result

        plan = result['data']['createInstallmentPlan']['plan']
        assert Decimal(plan['downPayment']) == Decimal('150000.00')
        assert plan['numberOfPayments'] == 3
        assert plan['status'] == 'active'

    def test_invalid_installment_plan(self, graphql_client, test_order):
        """Test creating installment plan with down payment > total"""
        order_id = to_global_id('Order', test_order.id)

        mutation = f"""
            mutation {{
                createInstallmentPlan(input: {{
                    orderId: "{order_id}"
                    downPayment: "600000.00"
                    numberOfPayments: 3
                    paymentFrequency: "monthly"
                }}) {{
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        plan_result = result['data']['createInstallmentPlan']

        assert len(plan_result['errors']) > 0


@pytest.mark.django_db
class TestProductComparisonMutations:
    """Test product comparison mutations"""

    def test_add_to_comparison(self, graphql_client):
        """Test adding product to comparison list"""
        from saleor.product.models import Product, ProductType

        # Create test product
        product_type = ProductType.objects.create(name='Electronics')
        product = Product.objects.create(
            name='Test Phone',
            product_type=product_type,
            is_published=True
        )

        product_id = to_global_id('Product', product.id)

        mutation = f"""
            mutation {{
                addToComparison(input: {{
                    productId: "{product_id}"
                }}) {{
                    comparison {{
                        id
                        product {{
                            name
                        }}
                    }}
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert 'errors' not in result

        comparison = result['data']['addToComparison']['comparison']
        assert comparison['product']['name'] == 'Test Phone'

    def test_remove_from_comparison(self, graphql_client):
        """Test removing product from comparison"""
        from saleor.product.models import Product, ProductType
        from uganda_backend_code.models.uganda_models import ProductComparison

        # Create test data
        product_type = ProductType.objects.create(name='Electronics')
        product = Product.objects.create(
            name='Test Phone',
            product_type=product_type,
            is_published=True
        )

        comparison = ProductComparison.objects.create(
            product=product,
            session_id='test_session_123'
        )

        comparison_id = to_global_id('ProductComparison', comparison.id)

        mutation = f"""
            mutation {{
                removeFromComparison(input: {{
                    comparisonId: "{comparison_id}"
                }}) {{
                    success
                    errors {{
                        field
                        message
                    }}
                }}
            }}
        """

        result = graphql_client.execute(mutation)
        assert 'errors' not in result
        assert result['data']['removeFromComparison']['success'] is True
