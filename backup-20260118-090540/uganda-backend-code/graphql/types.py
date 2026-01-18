"""
GraphQL Types for Uganda Platform
Add these to your Saleor GraphQL schema
"""

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
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


# =============================================================================
# OBJECT TYPES
# =============================================================================

class UgandaDistrictType(DjangoObjectType):
    """Uganda District with delivery information"""

    class Meta:
        model = UgandaDistrict
        fields = (
            'id', 'name', 'region', 'delivery_available',
            'delivery_fee', 'estimated_delivery_days',
            'sub_areas', 'is_active', 'created_at', 'updated_at'
        )
        interfaces = (relay.Node,)

    delivery_fee_display = graphene.String()

    def resolve_delivery_fee_display(root, info):
        """Format delivery fee as 'UGX 10,000'"""
        return f"UGX {root.delivery_fee:,.0f}"


class OrderDeliveryUgandaType(DjangoObjectType):
    """Delivery details for Uganda orders"""

    class Meta:
        model = OrderDeliveryUganda
        fields = (
            'id', 'order', 'district', 'sub_area', 'street_address',
            'landmark', 'recipient_name', 'recipient_phone',
            'alternative_phone', 'delivery_method', 'delivery_instructions',
            'pickup_ready_at', 'picked_up_at', 'delivery_fee',
            'estimated_delivery_date', 'actual_delivery_date',
            'delivered_by_name', 'delivered_by_phone', 'status',
            'delivery_notes', 'created_at', 'updated_at'
        )
        interfaces = (relay.Node,)

    status_display = graphene.String()
    delivery_method_display = graphene.String()

    def resolve_status_display(root, info):
        return root.get_status_display()

    def resolve_delivery_method_display(root, info):
        return root.get_delivery_method_display()


class MobileMoneyTransactionType(DjangoObjectType):
    """Mobile Money transaction details"""

    class Meta:
        model = MobileMoneyTransaction
        fields = (
            'id', 'order', 'provider', 'phone_number',
            'transaction_reference', 'amount', 'currency',
            'status', 'payment_method', 'initiated_at',
            'completed_at', 'verified_by_staff', 'verified_at',
            'provider_response', 'error_message', 'notes',
            'created_at', 'updated_at'
        )
        interfaces = (relay.Node,)

    provider_display = graphene.String()
    status_display = graphene.String()
    amount_display = graphene.String()

    def resolve_provider_display(root, info):
        return root.get_provider_display()

    def resolve_status_display(root, info):
        return root.get_status_display()

    def resolve_amount_display(root, info):
        return f"UGX {root.amount:,.0f}"


class SMSNotificationType(DjangoObjectType):
    """SMS notification record"""

    class Meta:
        model = SMSNotification
        fields = (
            'id', 'recipient_phone', 'message', 'notification_type',
            'order', 'user', 'provider', 'status', 'sent_at',
            'delivered_at', 'provider_message_id', 'provider_response',
            'error_message', 'cost', 'retry_count', 'max_retries',
            'created_at', 'updated_at'
        )
        interfaces = (relay.Node,)

    status_display = graphene.String()
    notification_type_display = graphene.String()

    def resolve_status_display(root, info):
        return root.get_status_display()

    def resolve_notification_type_display(root, info):
        return root.get_notification_type_display()


class ProductSerialNumberType(DjangoObjectType):
    """Product serial/IMEI tracking"""

    class Meta:
        model = ProductSerialNumber
        fields = (
            'id', 'variant', 'serial_number', 'serial_type',
            'status', 'purchase_date', 'sold_in_order', 'sold_date',
            'warranty_expires_at', 'notes', 'created_at', 'updated_at'
        )
        interfaces = (relay.Node,)

    status_display = graphene.String()
    serial_type_display = graphene.String()
    is_under_warranty = graphene.Boolean()

    def resolve_status_display(root, info):
        return root.get_status_display()

    def resolve_serial_type_display(root, info):
        return root.get_serial_type_display()

    def resolve_is_under_warranty(root, info):
        from django.utils import timezone
        if root.warranty_expires_at:
            return root.warranty_expires_at > timezone.now().date()
        return False


class ProductComparisonType(DjangoObjectType):
    """Product comparison list"""

    class Meta:
        model = ProductComparison
        fields = (
            'id', 'user', 'session_id', 'product_ids',
            'created_at', 'updated_at'
        )
        interfaces = (relay.Node,)

    products = graphene.List('saleor.graphql.product.types.Product')

    def resolve_products(root, info):
        from saleor.product.models import Product
        return Product.objects.filter(id__in=root.product_ids)


class InstallmentPlanType(DjangoObjectType):
    """Installment payment plan"""

    class Meta:
        model = InstallmentPlan
        fields = (
            'id', 'order', 'total_amount', 'down_payment',
            'remaining_balance', 'installment_amount',
            'number_of_installments', 'installment_frequency',
            'status', 'paid_installments', 'next_payment_due_date',
            'interest_rate', 'customer_national_id',
            'customer_id_photo_url', 'guarantor_name',
            'guarantor_phone', 'guarantor_relationship', 'notes',
            'created_at', 'updated_at'
        )
        interfaces = (relay.Node,)

    status_display = graphene.String()
    frequency_display = graphene.String()
    progress_percentage = graphene.Float()
    payments = graphene.List(lambda: InstallmentPaymentType)

    def resolve_status_display(root, info):
        return root.get_status_display()

    def resolve_frequency_display(root, info):
        return root.get_installment_frequency_display()

    def resolve_progress_percentage(root, info):
        if root.number_of_installments > 0:
            return (root.paid_installments / root.number_of_installments) * 100
        return 0

    def resolve_payments(root, info):
        return root.payments.all().order_by('installment_number')


class InstallmentPaymentType(DjangoObjectType):
    """Individual installment payment"""

    class Meta:
        model = InstallmentPayment
        fields = (
            'id', 'plan', 'installment_number', 'amount_due',
            'amount_paid', 'due_date', 'paid_date', 'payment_method',
            'payment_reference', 'status', 'late_fee', 'notes',
            'created_at', 'updated_at'
        )
        interfaces = (relay.Node,)

    status_display = graphene.String()
    is_overdue = graphene.Boolean()
    days_overdue = graphene.Int()

    def resolve_status_display(root, info):
        return root.get_status_display()

    def resolve_is_overdue(root, info):
        from django.utils import timezone
        if root.status == 'pending':
            return root.due_date < timezone.now().date()
        return False

    def resolve_days_overdue(root, info):
        from django.utils import timezone
        if root.status == 'pending' and root.due_date < timezone.now().date():
            delta = timezone.now().date() - root.due_date
            return delta.days
        return 0


class ShopInformationType(DjangoObjectType):
    """Shop configuration and information"""

    class Meta:
        model = ShopInformation
        fields = (
            'id', 'shop_name', 'tagline', 'phone_number',
            'alternative_phone', 'whatsapp_number', 'email',
            'physical_address', 'district', 'landmark',
            'google_maps_link', 'google_maps_embed', 'operating_hours',
            'facebook_page', 'instagram_handle', 'twitter_handle',
            'tiktok_handle', 'youtube_channel', 'return_policy',
            'warranty_policy', 'privacy_policy', 'terms_and_conditions',
            'bank_name', 'account_name', 'account_number', 'branch',
            'mtn_momo_name', 'mtn_momo_number', 'airtel_money_name',
            'airtel_money_number', 'about_text', 'about_image_url',
            'logo_url', 'favicon_url', 'meta_description',
            'meta_keywords', 'is_active', 'created_at', 'updated_at'
        )

    is_open_now = graphene.Boolean()
    todays_hours = graphene.String()

    def resolve_is_open_now(root, info):
        """Check if shop is currently open"""
        from django.utils import timezone
        import json

        now = timezone.now()
        day_name = now.strftime('%A').lower()

        if not root.operating_hours:
            return False

        day_hours = root.operating_hours.get(day_name, {})

        if day_hours.get('closed'):
            return False

        if 'open' in day_hours and 'close' in day_hours:
            from datetime import datetime
            current_time = now.time()
            open_time = datetime.strptime(day_hours['open'], '%H:%M').time()
            close_time = datetime.strptime(day_hours['close'], '%H:%M').time()

            return open_time <= current_time <= close_time

        return False

    def resolve_todays_hours(root, info):
        """Get today's operating hours"""
        from django.utils import timezone

        now = timezone.now()
        day_name = now.strftime('%A').lower()

        if not root.operating_hours:
            return "Hours not set"

        day_hours = root.operating_hours.get(day_name, {})

        if day_hours.get('closed'):
            return "Closed"

        if 'open' in day_hours and 'close' in day_hours:
            return f"{day_hours['open']} - {day_hours['close']}"

        return "Hours not set"


# =============================================================================
# INPUT TYPES
# =============================================================================

class UgandaDistrictFilterInput(graphene.InputObjectType):
    """Filter Uganda districts"""
    region = graphene.String()
    delivery_available = graphene.Boolean()
    name_contains = graphene.String()


class MobileMoneyPaymentInput(graphene.InputObjectType):
    """Input for initiating mobile money payment"""
    order_id = graphene.ID(required=True)
    provider = graphene.String(required=True)  # 'mtn_momo' or 'airtel_money'
    phone_number = graphene.String(required=True)
    amount = graphene.Decimal(required=True)


class DeliveryDetailsInput(graphene.InputObjectType):
    """Input for delivery details"""
    district_id = graphene.ID(required=True)
    sub_area = graphene.String()
    street_address = graphene.String(required=True)
    landmark = graphene.String()
    recipient_name = graphene.String(required=True)
    recipient_phone = graphene.String(required=True)
    alternative_phone = graphene.String()
    delivery_method = graphene.String(required=True)
    delivery_instructions = graphene.String()


class InstallmentPlanInput(graphene.InputObjectType):
    """Input for creating installment plan"""
    order_id = graphene.ID(required=True)
    down_payment = graphene.Decimal(required=True)
    number_of_installments = graphene.Int(required=True)
    installment_frequency = graphene.String()  # 'weekly' or 'monthly'
    customer_national_id = graphene.String()
    guarantor_name = graphene.String()
    guarantor_phone = graphene.String()
    guarantor_relationship = graphene.String()


# =============================================================================
# ENUMS
# =============================================================================

class UgandaRegionEnum(graphene.Enum):
    CENTRAL = 'Central'
    EASTERN = 'Eastern'
    NORTHERN = 'Northern'
    WESTERN = 'Western'


class MobileMoneyProviderEnum(graphene.Enum):
    MTN_MOMO = 'mtn_momo'
    AIRTEL_MONEY = 'airtel_money'


class PaymentStatusEnum(graphene.Enum):
    PENDING = 'pending'
    SUCCESSFUL = 'successful'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class DeliveryStatusEnum(graphene.Enum):
    PENDING = 'pending'
    READY_FOR_PICKUP = 'ready_for_pickup'
    OUT_FOR_DELIVERY = 'out_for_delivery'
    DELIVERED = 'delivered'
    FAILED = 'failed'


class DeliveryMethodEnum(graphene.Enum):
    SHOP_PICKUP = 'shop_pickup'
    HOME_DELIVERY = 'home_delivery'
    OFFICE_DELIVERY = 'office_delivery'
