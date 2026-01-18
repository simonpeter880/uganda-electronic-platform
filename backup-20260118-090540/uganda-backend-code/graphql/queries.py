"""
GraphQL Queries for Uganda Platform
"""

import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from .types import (
    UgandaDistrictType,
    OrderDeliveryUgandaType,
    MobileMoneyTransactionType,
    SMSNotificationType,
    ProductSerialNumberType,
    ProductComparisonType,
    InstallmentPlanType,
    InstallmentPaymentType,
    ShopInformationType,
    UgandaDistrictFilterInput,
)
from ..models import (
    UgandaDistrict,
    OrderDeliveryUganda,
    MobileMoneyTransaction,
    SMSNotification,
    ProductSerialNumber,
    ProductComparison,
    InstallmentPlan,
    InstallmentPayment,
    ShopInformation,
)


class UgandaQuery(graphene.ObjectType):
    """Uganda-specific queries"""

    # Districts
    uganda_districts = graphene.List(
        UgandaDistrictType,
        region=graphene.String(),
        delivery_available=graphene.Boolean(),
        name_contains=graphene.String(),
        description="Get list of Uganda districts with delivery information"
    )
    uganda_district = graphene.Field(
        UgandaDistrictType,
        id=graphene.ID(required=True),
        description="Get specific Uganda district by ID"
    )
    uganda_district_by_name = graphene.Field(
        UgandaDistrictType,
        name=graphene.String(required=True),
        description="Get district by name (e.g., 'Kampala')"
    )

    # Delivery
    order_delivery = graphene.Field(
        OrderDeliveryUgandaType,
        order_id=graphene.ID(required=True),
        description="Get delivery details for an order"
    )

    # Mobile Money
    mobile_money_transactions = graphene.List(
        MobileMoneyTransactionType,
        order_id=graphene.ID(),
        status=graphene.String(),
        provider=graphene.String(),
        description="Get mobile money transactions"
    )
    mobile_money_transaction = graphene.Field(
        MobileMoneyTransactionType,
        id=graphene.ID(required=True),
        description="Get specific mobile money transaction"
    )

    # SMS
    sms_notifications = graphene.List(
        SMSNotificationType,
        order_id=graphene.ID(),
        phone_number=graphene.String(),
        status=graphene.String(),
        description="Get SMS notifications"
    )

    # Serial Numbers
    product_serial_numbers = graphene.List(
        ProductSerialNumberType,
        variant_id=graphene.ID(),
        status=graphene.String(),
        serial_number=graphene.String(),
        description="Get product serial numbers/IMEI"
    )

    # Installments
    installment_plan = graphene.Field(
        InstallmentPlanType,
        order_id=graphene.ID(required=True),
        description="Get installment plan for an order"
    )
    my_installment_plans = graphene.List(
        InstallmentPlanType,
        description="Get current user's installment plans"
    )

    # Shop Info
    shop_information = graphene.Field(
        ShopInformationType,
        description="Get shop information and configuration"
    )

    # Product Comparison
    my_product_comparison = graphene.Field(
        ProductComparisonType,
        description="Get current user's product comparison list"
    )

    # =========================================================================
    # RESOLVERS
    # =========================================================================

    def resolve_uganda_districts(self, info, region=None, delivery_available=None, name_contains=None):
        """Get Uganda districts with optional filters"""
        qs = UgandaDistrict.objects.filter(is_active=True)

        if region:
            qs = qs.filter(region=region)

        if delivery_available is not None:
            qs = qs.filter(delivery_available=delivery_available)

        if name_contains:
            qs = qs.filter(name__icontains=name_contains)

        return qs.order_by('name')

    def resolve_uganda_district(self, info, id):
        """Get specific district by ID"""
        try:
            return UgandaDistrict.objects.get(pk=id)
        except UgandaDistrict.DoesNotExist:
            return None

    def resolve_uganda_district_by_name(self, info, name):
        """Get district by name"""
        try:
            return UgandaDistrict.objects.get(name__iexact=name)
        except UgandaDistrict.DoesNotExist:
            return None

    def resolve_order_delivery(self, info, order_id):
        """Get delivery details for an order"""
        try:
            return OrderDeliveryUganda.objects.select_related(
                'order', 'district'
            ).get(order_id=order_id)
        except OrderDeliveryUganda.DoesNotExist:
            return None

    def resolve_mobile_money_transactions(
        self, info, order_id=None, status=None, provider=None
    ):
        """Get mobile money transactions"""
        qs = MobileMoneyTransaction.objects.select_related('order')

        if order_id:
            qs = qs.filter(order_id=order_id)

        if status:
            qs = qs.filter(status=status)

        if provider:
            qs = qs.filter(provider=provider)

        return qs.order_by('-created_at')

    def resolve_mobile_money_transaction(self, info, id):
        """Get specific transaction"""
        try:
            return MobileMoneyTransaction.objects.select_related('order').get(pk=id)
        except MobileMoneyTransaction.DoesNotExist:
            return None

    def resolve_sms_notifications(
        self, info, order_id=None, phone_number=None, status=None
    ):
        """Get SMS notifications"""
        qs = SMSNotification.objects.all()

        if order_id:
            qs = qs.filter(order_id=order_id)

        if phone_number:
            qs = qs.filter(recipient_phone=phone_number)

        if status:
            qs = qs.filter(status=status)

        return qs.order_by('-created_at')[:50]  # Limit to 50 most recent

    def resolve_product_serial_numbers(
        self, info, variant_id=None, status=None, serial_number=None
    ):
        """Get product serial numbers"""
        qs = ProductSerialNumber.objects.select_related('variant')

        if variant_id:
            qs = qs.filter(variant_id=variant_id)

        if status:
            qs = qs.filter(status=status)

        if serial_number:
            qs = qs.filter(serial_number__iexact=serial_number)

        return qs.order_by('-created_at')

    def resolve_installment_plan(self, info, order_id):
        """Get installment plan for order"""
        try:
            return InstallmentPlan.objects.select_related('order').get(order_id=order_id)
        except InstallmentPlan.DoesNotExist:
            return None

    def resolve_my_installment_plans(self, info):
        """Get current user's installment plans"""
        user = info.context.user

        if not user.is_authenticated:
            return []

        return InstallmentPlan.objects.filter(
            order__user=user
        ).select_related('order').order_by('-created_at')

    def resolve_shop_information(self, info):
        """Get shop information"""
        try:
            return ShopInformation.objects.select_related('district').get(id=1)
        except ShopInformation.DoesNotExist:
            return None

    def resolve_my_product_comparison(self, info):
        """Get current user's product comparison"""
        user = info.context.user

        if user.is_authenticated:
            try:
                return ProductComparison.objects.get(user=user)
            except ProductComparison.DoesNotExist:
                return None
        else:
            # For anonymous users, use session
            session_id = info.context.session.session_key
            if session_id:
                try:
                    return ProductComparison.objects.get(session_id=session_id)
                except ProductComparison.DoesNotExist:
                    return None

        return None


# Example query usage:
"""
query GetUgandaDistricts {
  ugandaDistricts(region: "Central") {
    id
    name
    region
    deliveryFee
    deliveryFeeDisplay
    estimatedDeliveryDays
    subAreas
  }
}

query GetOrderDelivery {
  orderDelivery(orderId: "order-uuid") {
    id
    district {
      name
      deliveryFee
    }
    recipientName
    recipientPhone
    streetAddress
    landmark
    status
    statusDisplay
    deliveryFee
    estimatedDeliveryDate
  }
}

query GetMobileMoneyTransactions {
  mobileMoneyTransactions(orderId: "order-uuid") {
    id
    provider
    providerDisplay
    phoneNumber
    amount
    amountDisplay
    status
    statusDisplay
    transactionReference
    initiatedAt
    completedAt
  }
}

query GetInstallmentPlan {
  installmentPlan(orderId: "order-uuid") {
    id
    totalAmount
    downPayment
    remainingBalance
    installmentAmount
    numberOfInstallments
    paidInstallments
    progressPercentage
    status
    nextPaymentDueDate
    payments {
      installmentNumber
      amountDue
      dueDate
      status
      isOverdue
      daysOverdue
    }
  }
}

query GetShopInfo {
  shopInformation {
    shopName
    phoneNumber
    whatsappNumber
    email
    physicalAddress
    landmark
    isOpenNow
    todaysHours
    operatingHours
    facebookPage
    instagramHandle
  }
}
"""
