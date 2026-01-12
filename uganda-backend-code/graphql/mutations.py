"""
GraphQL Mutations for Uganda Platform
"""

import graphene
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from .types import (
    MobileMoneyTransactionType,
    OrderDeliveryUgandaType,
    InstallmentPlanType,
    ProductComparisonType,
    SMSNotificationType,
    MobileMoneyPaymentInput,
    DeliveryDetailsInput,
    InstallmentPlanInput,
)
from ..models import (
    UgandaDistrict,
    OrderDeliveryUganda,
    MobileMoneyTransaction,
    InstallmentPlan,
    InstallmentPayment,
    ProductComparison,
    SMSNotification,
)
from ..services.mobile_money import MobileMoneyService, MobileMoneyError
from ..services.sms_service import SMSService, SMSError


# =============================================================================
# MOBILE MONEY MUTATIONS
# =============================================================================

class InitiateMobileMoneyPayment(graphene.Mutation):
    """Initiate a Mobile Money payment"""

    class Arguments:
        input = MobileMoneyPaymentInput(required=True)

    transaction = graphene.Field(MobileMoneyTransactionType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        from saleor.order.models import Order

        errors = []

        try:
            # Get order
            order = Order.objects.get(pk=input.order_id)

            # Validate amount matches order total
            if input.amount != order.total.gross.amount:
                errors.append(f"Amount mismatch: expected {order.total.gross.amount}")
                return InitiateMobileMoneyPayment(
                    transaction=None,
                    success=False,
                    errors=errors
                )

            # Create transaction record
            momo_transaction = MobileMoneyTransaction.objects.create(
                order=order,
                provider=input.provider,
                phone_number=input.phone_number,
                amount=input.amount,
                currency='UGX',
                status='pending',
                payment_method='mobile_money'
            )

            # Initiate payment with provider
            momo_service = MobileMoneyService()

            try:
                tx_id, response = momo_service.initiate_payment(
                    provider=input.provider,
                    phone_number=input.phone_number,
                    amount=input.amount,
                    order_number=str(order.number),
                    payer_message=f"Payment for order #{order.number}"
                )

                # Update transaction with provider response
                momo_transaction.transaction_reference = tx_id
                momo_transaction.provider_response = response
                momo_transaction.save()

                # Send SMS confirmation
                try:
                    sms_service = SMSService()
                    sms_service.send_payment_confirmation(
                        phone_number=input.phone_number,
                        order_number=str(order.number),
                        amount=f"{input.amount:,.0f}"
                    )
                except Exception as sms_error:
                    # Log but don't fail the payment
                    print(f"SMS failed: {sms_error}")

                return InitiateMobileMoneyPayment(
                    transaction=momo_transaction,
                    success=True,
                    errors=[]
                )

            except MobileMoneyError as e:
                momo_transaction.status = 'failed'
                momo_transaction.error_message = str(e)
                momo_transaction.save()

                errors.append(str(e))
                return InitiateMobileMoneyPayment(
                    transaction=momo_transaction,
                    success=False,
                    errors=errors
                )

        except Order.DoesNotExist:
            errors.append("Order not found")
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")

        return InitiateMobileMoneyPayment(
            transaction=None,
            success=False,
            errors=errors
        )


class CheckMobileMoneyPaymentStatus(graphene.Mutation):
    """Check status of a Mobile Money payment"""

    class Arguments:
        transaction_id = graphene.ID(required=True)

    transaction = graphene.Field(MobileMoneyTransactionType)
    success = graphene.Boolean()
    is_paid = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, transaction_id):
        errors = []

        try:
            transaction = MobileMoneyTransaction.objects.get(pk=transaction_id)

            # Check status with provider
            momo_service = MobileMoneyService()

            status_data = momo_service.check_payment_status(
                transaction.provider,
                transaction.transaction_reference
            )

            # Update transaction
            status = status_data.get('status', '').upper()

            if status in ['SUCCESSFUL', 'TS']:
                transaction.status = 'successful'
                transaction.completed_at = timezone.now()

                # Mark order as paid
                order = transaction.order
                order.payment_verified = True
                order.payment_verified_at = timezone.now()
                order.save()

            elif status in ['FAILED', 'TF']:
                transaction.status = 'failed'
                transaction.error_message = status_data.get('reason', 'Payment failed')

            transaction.provider_response = status_data
            transaction.save()

            is_paid = transaction.status == 'successful'

            return CheckMobileMoneyPaymentStatus(
                transaction=transaction,
                success=True,
                is_paid=is_paid,
                errors=[]
            )

        except MobileMoneyTransaction.DoesNotExist:
            errors.append("Transaction not found")
        except Exception as e:
            errors.append(f"Error checking status: {str(e)}")

        return CheckMobileMoneyPaymentStatus(
            transaction=None,
            success=False,
            is_paid=False,
            errors=errors
        )


# =============================================================================
# DELIVERY MUTATIONS
# =============================================================================

class CreateOrderDelivery(graphene.Mutation):
    """Create delivery details for an order"""

    class Arguments:
        input = DeliveryDetailsInput(required=True)

    delivery = graphene.Field(OrderDeliveryUgandaType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        from saleor.order.models import Order

        errors = []

        try:
            # Get order
            order = Order.objects.get(pk=input.order_id)

            # Get district
            district = UgandaDistrict.objects.get(pk=input.district_id)

            # Create delivery record
            delivery = OrderDeliveryUganda.objects.create(
                order=order,
                district=district,
                sub_area=input.sub_area or '',
                street_address=input.street_address,
                landmark=input.landmark or '',
                recipient_name=input.recipient_name,
                recipient_phone=input.recipient_phone,
                alternative_phone=input.alternative_phone or '',
                delivery_method=input.delivery_method,
                delivery_instructions=input.delivery_instructions or '',
                delivery_fee=district.delivery_fee,
                estimated_delivery_date=timezone.now().date() + timezone.timedelta(
                    days=district.estimated_delivery_days
                ),
                status='pending'
            )

            # Generate verification code for pickup
            if input.delivery_method == 'shop_pickup':
                import random
                verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                order.verification_code = verification_code
                order.save()

            # Send SMS notification
            try:
                sms_service = SMSService()
                sms_service.send_order_confirmation(
                    phone_number=input.recipient_phone,
                    order_number=str(order.number),
                    total_amount=f"{order.total.gross.amount:,.0f}"
                )
            except Exception as sms_error:
                print(f"SMS failed: {sms_error}")

            return CreateOrderDelivery(
                delivery=delivery,
                success=True,
                errors=[]
            )

        except Order.DoesNotExist:
            errors.append("Order not found")
        except UgandaDistrict.DoesNotExist:
            errors.append("District not found")
        except Exception as e:
            errors.append(f"Error: {str(e)}")

        return CreateOrderDelivery(
            delivery=None,
            success=False,
            errors=errors
        )


class UpdateDeliveryStatus(graphene.Mutation):
    """Update delivery status"""

    class Arguments:
        delivery_id = graphene.ID(required=True)
        status = graphene.String(required=True)
        notes = graphene.String()

    delivery = graphene.Field(OrderDeliveryUgandaType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, delivery_id, status, notes=None):
        errors = []

        try:
            delivery = OrderDeliveryUganda.objects.get(pk=delivery_id)
            delivery.status = status

            if notes:
                delivery.delivery_notes = notes

            # Set timestamps based on status
            if status == 'ready_for_pickup':
                delivery.pickup_ready_at = timezone.now()

                # Send SMS
                try:
                    sms_service = SMSService()
                    sms_service.send_ready_for_pickup(
                        phone_number=delivery.recipient_phone,
                        order_number=str(delivery.order.number),
                        verification_code=delivery.order.verification_code or 'N/A',
                        shop_address=ShopInformation.objects.get(id=1).physical_address
                    )
                except Exception:
                    pass

            elif status == 'out_for_delivery':
                # Send SMS
                try:
                    sms_service = SMSService()
                    sms_service.send_out_for_delivery(
                        phone_number=delivery.recipient_phone,
                        order_number=str(delivery.order.number),
                        estimated_time="within 2 hours"
                    )
                except Exception:
                    pass

            elif status == 'delivered':
                delivery.actual_delivery_date = timezone.now().date()

                # Send SMS
                try:
                    sms_service = SMSService()
                    sms_service.send_delivered(
                        phone_number=delivery.recipient_phone,
                        order_number=str(delivery.order.number)
                    )
                except Exception:
                    pass

            delivery.save()

            return UpdateDeliveryStatus(
                delivery=delivery,
                success=True,
                errors=[]
            )

        except OrderDeliveryUganda.DoesNotExist:
            errors.append("Delivery not found")
        except Exception as e:
            errors.append(f"Error: {str(e)}")

        return UpdateDeliveryStatus(
            delivery=None,
            success=False,
            errors=errors
        )


# =============================================================================
# INSTALLMENT MUTATIONS
# =============================================================================

class CreateInstallmentPlan(graphene.Mutation):
    """Create an installment payment plan for an order"""

    class Arguments:
        input = InstallmentPlanInput(required=True)

    plan = graphene.Field(InstallmentPlanType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, input):
        from saleor.order.models import Order

        errors = []

        try:
            # Get order
            order = Order.objects.get(pk=input.order_id)

            total_amount = order.total.gross.amount
            down_payment = input.down_payment
            remaining_balance = total_amount - down_payment

            if remaining_balance <= 0:
                errors.append("Down payment must be less than total amount")
                return CreateInstallmentPlan(plan=None, success=False, errors=errors)

            # Calculate installment amount
            installment_amount = remaining_balance / input.number_of_installments

            # Create installment plan
            plan = InstallmentPlan.objects.create(
                order=order,
                total_amount=total_amount,
                down_payment=down_payment,
                remaining_balance=remaining_balance,
                installment_amount=installment_amount,
                number_of_installments=input.number_of_installments,
                installment_frequency=input.installment_frequency or 'monthly',
                status='active',
                paid_installments=0,
                next_payment_due_date=timezone.now().date() + timezone.timedelta(days=30),
                customer_national_id=input.customer_national_id or '',
                guarantor_name=input.guarantor_name or '',
                guarantor_phone=input.guarantor_phone or '',
                guarantor_relationship=input.guarantor_relationship or ''
            )

            # Create individual payment records
            current_date = timezone.now().date()
            frequency_days = 7 if input.installment_frequency == 'weekly' else 30

            for i in range(1, input.number_of_installments + 1):
                due_date = current_date + timezone.timedelta(days=frequency_days * i)

                InstallmentPayment.objects.create(
                    plan=plan,
                    installment_number=i,
                    amount_due=installment_amount,
                    due_date=due_date,
                    status='pending'
                )

            return CreateInstallmentPlan(
                plan=plan,
                success=True,
                errors=[]
            )

        except Order.DoesNotExist:
            errors.append("Order not found")
        except Exception as e:
            errors.append(f"Error: {str(e)}")

        return CreateInstallmentPlan(
            plan=None,
            success=False,
            errors=errors
        )


# =============================================================================
# PRODUCT COMPARISON MUTATIONS
# =============================================================================

class AddToComparison(graphene.Mutation):
    """Add product to comparison list"""

    class Arguments:
        product_id = graphene.ID(required=True)

    comparison = graphene.Field(ProductComparisonType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, product_id):
        import uuid

        user = info.context.user
        errors = []

        try:
            # Get or create comparison list
            if user.is_authenticated:
                comparison, created = ProductComparison.objects.get_or_create(
                    user=user,
                    defaults={'id': uuid.uuid4()}
                )
            else:
                session_id = info.context.session.session_key
                if not session_id:
                    info.context.session.create()
                    session_id = info.context.session.session_key

                comparison, created = ProductComparison.objects.get_or_create(
                    session_id=session_id,
                    defaults={'id': uuid.uuid4()}
                )

            # Add product if not already in list
            product_id_int = int(product_id)
            if product_id_int not in comparison.product_ids:
                comparison.product_ids.append(product_id_int)
                comparison.save()

            return AddToComparison(
                comparison=comparison,
                success=True,
                errors=[]
            )

        except Exception as e:
            errors.append(f"Error: {str(e)}")

        return AddToComparison(
            comparison=None,
            success=False,
            errors=errors
        )


class RemoveFromComparison(graphene.Mutation):
    """Remove product from comparison list"""

    class Arguments:
        product_id = graphene.ID(required=True)

    comparison = graphene.Field(ProductComparisonType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, product_id):
        user = info.context.user
        errors = []

        try:
            # Get comparison list
            if user.is_authenticated:
                comparison = ProductComparison.objects.get(user=user)
            else:
                session_id = info.context.session.session_key
                comparison = ProductComparison.objects.get(session_id=session_id)

            # Remove product
            product_id_int = int(product_id)
            if product_id_int in comparison.product_ids:
                comparison.product_ids.remove(product_id_int)
                comparison.save()

            return RemoveFromComparison(
                comparison=comparison,
                success=True,
                errors=[]
            )

        except ProductComparison.DoesNotExist:
            errors.append("Comparison list not found")
        except Exception as e:
            errors.append(f"Error: {str(e)}")

        return RemoveFromComparison(
            comparison=None,
            success=False,
            errors=errors
        )


# =============================================================================
# MUTATION ROOT
# =============================================================================

class UgandaMutations(graphene.ObjectType):
    """Uganda platform mutations"""

    # Mobile Money
    initiate_mobile_money_payment = InitiateMobileMoneyPayment.Field()
    check_mobile_money_payment_status = CheckMobileMoneyPaymentStatus.Field()

    # Delivery
    create_order_delivery = CreateOrderDelivery.Field()
    update_delivery_status = UpdateDeliveryStatus.Field()

    # Installments
    create_installment_plan = CreateInstallmentPlan.Field()

    # Product Comparison
    add_to_comparison = AddToComparison.Field()
    remove_from_comparison = RemoveFromComparison.Field()


# Example mutation usage:
"""
mutation InitiatePayment {
  initiateMobileMoneyPayment(input: {
    orderId: "order-uuid"
    provider: "mtn_momo"
    phoneNumber: "256700123456"
    amount: "50000"
  }) {
    transaction {
      id
      transactionReference
      status
      providerDisplay
    }
    success
    errors
  }
}

mutation CreateDelivery {
  createOrderDelivery(input: {
    orderId: "order-uuid"
    districtId: "1"
    streetAddress: "Plot 123, Kampala Road"
    landmark: "Near Shell Ntinda"
    recipientName: "John Doe"
    recipientPhone: "256700123456"
    deliveryMethod: "home_delivery"
  }) {
    delivery {
      id
      status
      deliveryFee
      estimatedDeliveryDate
    }
    success
    errors
  }
}

mutation CreateInstallments {
  createInstallmentPlan(input: {
    orderId: "order-uuid"
    downPayment: "100000"
    numberOfInstallments: 6
    installmentFrequency: "monthly"
    customerNationalId: "CM12345678"
    guarantorName: "Jane Doe"
    guarantorPhone: "256700987654"
  }) {
    plan {
      id
      installmentAmount
      nextPaymentDueDate
      payments {
        installmentNumber
        amountDue
        dueDate
      }
    }
    success
    errors
  }
}
"""
