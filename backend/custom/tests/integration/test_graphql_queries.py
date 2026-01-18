"""
Integration tests for Uganda GraphQL queries
"""
import pytest
from decimal import Decimal
from graphql_relay import to_global_id


@pytest.mark.django_db
class TestUgandaDistrictQueries:
    """Test Uganda district GraphQL queries"""

    def test_query_all_districts(self, graphql_client, uganda_district):
        """Test querying all Uganda districts"""
        query = """
            query {
                ugandaDistricts(first: 10) {
                    edges {
                        node {
                            id
                            name
                            region
                            deliveryFee
                            estimatedDeliveryDays
                            deliveryAvailable
                        }
                    }
                    totalCount
                }
            }
        """

        result = graphql_client.execute(query)
        assert 'errors' not in result
        assert result['data']['ugandaDistricts']['totalCount'] >= 1

        district = result['data']['ugandaDistricts']['edges'][0]['node']
        assert district['name'] == 'Kampala'
        assert district['region'] == 'Central'
        assert Decimal(district['deliveryFee']) == Decimal('10000.00')

    def test_query_district_by_id(self, graphql_client, uganda_district):
        """Test querying a specific district by ID"""
        district_id = to_global_id('UgandaDistrict', uganda_district.id)

        query = f"""
            query {{
                ugandaDistrict(id: "{district_id}") {{
                    id
                    name
                    region
                    deliveryFee
                    subAreas
                }}
            }}
        """

        result = graphql_client.execute(query)
        assert 'errors' not in result

        district = result['data']['ugandaDistrict']
        assert district['name'] == 'Kampala'
        assert 'Nakasero' in district['subAreas']

    def test_query_district_by_name(self, graphql_client, uganda_district):
        """Test querying district by name"""
        query = """
            query {
                ugandaDistrictByName(name: "Kampala") {
                    id
                    name
                    deliveryAvailable
                }
            }
        """

        result = graphql_client.execute(query)
        assert 'errors' not in result
        assert result['data']['ugandaDistrictByName']['name'] == 'Kampala'

    def test_filter_districts_by_region(self, graphql_client, uganda_district):
        """Test filtering districts by region"""
        query = """
            query {
                ugandaDistricts(first: 10, region: "Central") {
                    edges {
                        node {
                            name
                            region
                        }
                    }
                }
            }
        """

        result = graphql_client.execute(query)
        assert 'errors' not in result

        for edge in result['data']['ugandaDistricts']['edges']:
            assert edge['node']['region'] == 'Central'


@pytest.mark.django_db
class TestMobileMoneyQueries:
    """Test mobile money transaction queries"""

    def test_query_transactions(self, graphql_client, mobile_money_transaction, graphql_headers):
        """Test querying mobile money transactions"""
        query = """
            query {
                mobileMoneyTransactions(first: 10) {
                    edges {
                        node {
                            id
                            provider
                            phoneNumber
                            amount
                            status
                            transactionReference
                        }
                    }
                }
            }
        """

        result = graphql_client.execute(query, context_value={'headers': graphql_headers})
        assert 'errors' not in result

        transactions = result['data']['mobileMoneyTransactions']['edges']
        assert len(transactions) >= 1

        txn = transactions[0]['node']
        assert txn['provider'] == 'mtn_momo'
        assert txn['phoneNumber'] == '256700123456'

    def test_query_transaction_by_id(self, graphql_client, mobile_money_transaction, graphql_headers):
        """Test querying specific transaction"""
        txn_id = to_global_id('MobileMoneyTransaction', mobile_money_transaction.id)

        query = f"""
            query {{
                mobileMoneyTransaction(id: "{txn_id}") {{
                    id
                    transactionReference
                    status
                    amount
                }}
            }}
        """

        result = graphql_client.execute(query, context_value={'headers': graphql_headers})
        assert 'errors' not in result

        txn = result['data']['mobileMoneyTransaction']
        assert txn['transactionReference'] == 'MTN_TEST_12345'
        assert txn['status'] == 'pending'

    def test_filter_transactions_by_status(self, graphql_client, mobile_money_transaction):
        """Test filtering transactions by status"""
        query = """
            query {
                mobileMoneyTransactions(first: 10, status: "pending") {
                    edges {
                        node {
                            status
                        }
                    }
                }
            }
        """

        result = graphql_client.execute(query)
        assert 'errors' not in result

        for edge in result['data']['mobileMoneyTransactions']['edges']:
            assert edge['node']['status'] == 'pending'


@pytest.mark.django_db
class TestOrderDeliveryQueries:
    """Test order delivery queries"""

    def test_query_order_delivery(self, graphql_client, order_delivery, test_order):
        """Test querying order delivery details"""
        order_id = to_global_id('Order', test_order.id)

        query = f"""
            query {{
                orderDelivery(orderId: "{order_id}") {{
                    id
                    recipientName
                    recipientPhone
                    deliveryMethod
                    status
                    district {{
                        name
                        deliveryFee
                    }}
                }}
            }}
        """

        result = graphql_client.execute(query)
        assert 'errors' not in result

        delivery = result['data']['orderDelivery']
        assert delivery['recipientName'] == 'John Doe'
        assert delivery['recipientPhone'] == '256700123456'
        assert delivery['district']['name'] == 'Kampala'

    def test_query_delivery_status_tracking(self, graphql_client, order_delivery, test_order):
        """Test tracking delivery status"""
        # Update delivery status
        order_delivery.status = 'out_for_delivery'
        order_delivery.save()

        order_id = to_global_id('Order', test_order.id)

        query = f"""
            query {{
                orderDelivery(orderId: "{order_id}") {{
                    status
                    estimatedDeliveryDate
                }}
            }}
        """

        result = graphql_client.execute(query)
        assert 'errors' not in result
        assert result['data']['orderDelivery']['status'] == 'out_for_delivery'


@pytest.mark.django_db
class TestSMSNotificationQueries:
    """Test SMS notification queries"""

    def test_query_sms_notifications(self, graphql_client, graphql_headers):
        """Test querying SMS notifications"""
        from uganda_backend_code.models.uganda_models import SMSNotification

        # Create test SMS notification
        sms = SMSNotification.objects.create(
            recipient_phone='256700123456',
            message='Test order confirmation',
            notification_type='order_confirmation',
            provider='africas_talking',
            status='sent'
        )

        query = """
            query {
                smsNotifications(first: 10) {
                    edges {
                        node {
                            recipientPhone
                            message
                            notificationType
                            status
                        }
                    }
                }
            }
        """

        result = graphql_client.execute(query, context_value={'headers': graphql_headers})
        assert 'errors' not in result

        notifications = result['data']['smsNotifications']['edges']
        assert len(notifications) >= 1


@pytest.mark.django_db
class TestInstallmentQueries:
    """Test installment plan queries"""

    def test_query_installment_plan(self, graphql_client, test_order):
        """Test querying installment plans"""
        from uganda_backend_code.models.uganda_models import InstallmentPlan

        plan = InstallmentPlan.objects.create(
            order=test_order,
            down_payment=Decimal('100000.00'),
            remaining_amount=Decimal('400000.00'),
            number_of_payments=4,
            payment_frequency='monthly',
            status='active'
        )

        plan_id = to_global_id('InstallmentPlan', plan.id)

        query = f"""
            query {{
                installmentPlan(id: "{plan_id}") {{
                    id
                    downPayment
                    remainingAmount
                    numberOfPayments
                    paymentFrequency
                    status
                }}
            }}
        """

        result = graphql_client.execute(query)
        assert 'errors' not in result

        plan_data = result['data']['installmentPlan']
        assert Decimal(plan_data['downPayment']) == Decimal('100000.00')
        assert plan_data['numberOfPayments'] == 4
        assert plan_data['status'] == 'active'
