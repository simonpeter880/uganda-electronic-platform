"""
Django Admin for Uganda Platform
Register these in your Django admin
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
# UGANDA DISTRICT ADMIN
# =============================================================================

@admin.register(UgandaDistrict)
class UgandaDistrictAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'region', 'delivery_fee_display', 'estimated_delivery_days',
        'delivery_available', 'is_active'
    )
    list_filter = ('region', 'delivery_available', 'is_active')
    search_fields = ('name', 'sub_areas')
    ordering = ('name',)

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'region', 'is_active')
        }),
        (_('Delivery Configuration'), {
            'fields': (
                'delivery_available',
                'delivery_fee',
                'estimated_delivery_days',
                'sub_areas'
            )
        }),
    )

    def delivery_fee_display(self, obj):
        return f"UGX {obj.delivery_fee:,.0f}"
    delivery_fee_display.short_description = _('Delivery Fee')


# =============================================================================
# DELIVERY ADMIN
# =============================================================================

@admin.register(OrderDeliveryUganda)
class OrderDeliveryUgandaAdmin(admin.ModelAdmin):
    list_display = (
        'order_link', 'recipient_name', 'recipient_phone',
        'district', 'delivery_method', 'status',
        'estimated_delivery_date', 'created_at'
    )
    list_filter = ('status', 'delivery_method', 'district__region', 'created_at')
    search_fields = (
        'recipient_name', 'recipient_phone', 'order__number',
        'street_address', 'landmark'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Order Information'), {
            'fields': ('order', 'status')
        }),
        (_('Delivery Location'), {
            'fields': (
                'district', 'sub_area', 'street_address', 'landmark'
            )
        }),
        (_('Recipient Details'), {
            'fields': (
                'recipient_name', 'recipient_phone', 'alternative_phone'
            )
        }),
        (_('Delivery Details'), {
            'fields': (
                'delivery_method', 'delivery_instructions',
                'delivery_fee', 'estimated_delivery_date', 'actual_delivery_date'
            )
        }),
        (_('Pickup Details'), {
            'fields': ('pickup_ready_at', 'picked_up_at'),
            'classes': ('collapse',)
        }),
        (_('Delivery Personnel'), {
            'fields': ('delivered_by_name', 'delivered_by_phone'),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('delivery_notes',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_link(self, obj):
        url = reverse('admin:order_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.number)
    order_link.short_description = _('Order')


# =============================================================================
# MOBILE MONEY ADMIN
# =============================================================================

@admin.register(MobileMoneyTransaction)
class MobileMoneyTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'order_link', 'provider', 'phone_number', 'amount_display',
        'status', 'payment_method', 'verified_by_staff', 'initiated_at'
    )
    list_filter = (
        'status', 'provider', 'payment_method',
        'verified_by_staff', 'initiated_at'
    )
    search_fields = (
        'order__number', 'phone_number',
        'transaction_reference', 'notes'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'initiated_at',
        'completed_at', 'provider_response'
    )

    fieldsets = (
        (_('Transaction Details'), {
            'fields': (
                'order', 'provider', 'payment_method',
                'status', 'transaction_reference'
            )
        }),
        (_('Payment Information'), {
            'fields': (
                'phone_number', 'amount', 'currency'
            )
        }),
        (_('Verification'), {
            'fields': (
                'verified_by_staff', 'verified_at',
                'initiated_at', 'completed_at'
            )
        }),
        (_('Provider Response'), {
            'fields': ('provider_response', 'error_message'),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_verified', 'mark_as_successful']

    def order_link(self, obj):
        url = reverse('admin:order_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.number)
    order_link.short_description = _('Order')

    def amount_display(self, obj):
        return f"UGX {obj.amount:,.0f}"
    amount_display.short_description = _('Amount')

    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        queryset.update(verified_by_staff=True, verified_at=timezone.now())
    mark_as_verified.short_description = _('Mark as verified by staff')

    def mark_as_successful(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='successful', completed_at=timezone.now())
    mark_as_successful.short_description = _('Mark as successful')


# =============================================================================
# SMS NOTIFICATION ADMIN
# =============================================================================

@admin.register(SMSNotification)
class SMSNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient_phone', 'notification_type', 'status',
        'order_link', 'sent_at', 'delivered_at', 'cost'
    )
    list_filter = ('status', 'notification_type', 'provider', 'sent_at')
    search_fields = (
        'recipient_phone', 'message', 'order__number',
        'provider_message_id'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'sent_at',
        'delivered_at', 'provider_response'
    )

    fieldsets = (
        (_('Message Details'), {
            'fields': (
                'recipient_phone', 'message', 'notification_type'
            )
        }),
        (_('Related Objects'), {
            'fields': ('order', 'user')
        }),
        (_('Delivery Status'), {
            'fields': (
                'provider', 'status', 'sent_at', 'delivered_at',
                'provider_message_id', 'cost'
            )
        }),
        (_('Provider Response'), {
            'fields': ('provider_response', 'error_message'),
            'classes': ('collapse',)
        }),
        (_('Retry Configuration'), {
            'fields': ('retry_count', 'max_retries'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:order_order_change', args=[obj.order.pk])
            return format_html('<a href="{}">{}</a>', url, obj.order.number)
        return '-'
    order_link.short_description = _('Order')


# =============================================================================
# SERIAL NUMBER ADMIN
# =============================================================================

@admin.register(ProductSerialNumber)
class ProductSerialNumberAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number', 'serial_type', 'variant_link',
        'status', 'warranty_status', 'sold_date'
    )
    list_filter = ('status', 'serial_type', 'sold_date', 'warranty_expires_at')
    search_fields = (
        'serial_number', 'variant__sku', 'variant__name',
        'notes'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Serial Information'), {
            'fields': ('variant', 'serial_number', 'serial_type', 'status')
        }),
        (_('Purchase Details'), {
            'fields': ('purchase_date', 'sold_in_order', 'sold_date')
        }),
        (_('Warranty'), {
            'fields': ('warranty_expires_at',)
        }),
        (_('Notes'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def variant_link(self, obj):
        from django.contrib.admin.utils import quote
        url = reverse('admin:product_productvariant_change', args=[quote(obj.variant.pk)])
        return format_html('<a href="{}">{}</a>', url, obj.variant.name)
    variant_link.short_description = _('Variant')

    def warranty_status(self, obj):
        from django.utils import timezone
        if not obj.warranty_expires_at:
            return '-'

        if obj.warranty_expires_at > timezone.now().date():
            days_left = (obj.warranty_expires_at - timezone.now().date()).days
            return format_html(
                '<span style="color: green;">✓ Valid ({} days left)</span>',
                days_left
            )
        else:
            return format_html('<span style="color: red;">✗ Expired</span>')

    warranty_status.short_description = _('Warranty Status')


# =============================================================================
# INSTALLMENT ADMIN
# =============================================================================

class InstallmentPaymentInline(admin.TabularInline):
    model = InstallmentPayment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'installment_number', 'amount_due', 'amount_paid',
        'due_date', 'paid_date', 'status', 'late_fee'
    )


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = (
        'order_link', 'total_amount_display', 'down_payment_display',
        'installment_amount_display', 'paid_installments',
        'number_of_installments', 'status', 'next_payment_due_date'
    )
    list_filter = ('status', 'installment_frequency', 'created_at')
    search_fields = (
        'order__number', 'customer_national_id',
        'guarantor_name', 'guarantor_phone'
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [InstallmentPaymentInline]

    fieldsets = (
        (_('Order Information'), {
            'fields': ('order', 'status')
        }),
        (_('Plan Details'), {
            'fields': (
                'total_amount', 'down_payment', 'remaining_balance',
                'installment_amount', 'number_of_installments',
                'installment_frequency', 'interest_rate'
            )
        }),
        (_('Payment Tracking'), {
            'fields': ('paid_installments', 'next_payment_due_date')
        }),
        (_('Customer Verification'), {
            'fields': (
                'customer_national_id', 'customer_id_photo_url'
            ),
            'classes': ('collapse',)
        }),
        (_('Guarantor Information'), {
            'fields': (
                'guarantor_name', 'guarantor_phone', 'guarantor_relationship'
            ),
            'classes': ('collapse',)
        }),
        (_('Notes'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_link(self, obj):
        url = reverse('admin:order_order_change', args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.number)
    order_link.short_description = _('Order')

    def total_amount_display(self, obj):
        return f"UGX {obj.total_amount:,.0f}"
    total_amount_display.short_description = _('Total Amount')

    def down_payment_display(self, obj):
        return f"UGX {obj.down_payment:,.0f}"
    down_payment_display.short_description = _('Down Payment')

    def installment_amount_display(self, obj):
        return f"UGX {obj.installment_amount:,.0f}"
    installment_amount_display.short_description = _('Installment Amount')


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'plan_link', 'installment_number', 'amount_due_display',
        'due_date', 'status', 'paid_date', 'late_fee_display'
    )
    list_filter = ('status', 'due_date', 'paid_date')
    search_fields = ('plan__order__number', 'payment_reference')
    readonly_fields = ('created_at', 'updated_at')

    def plan_link(self, obj):
        url = reverse('admin:uganda_installmentplan_change', args=[obj.plan.pk])
        return format_html(
            '<a href="{}">Order #{}</a>',
            url, obj.plan.order.number
        )
    plan_link.short_description = _('Plan')

    def amount_due_display(self, obj):
        return f"UGX {obj.amount_due:,.0f}"
    amount_due_display.short_description = _('Amount Due')

    def late_fee_display(self, obj):
        return f"UGX {obj.late_fee:,.0f}" if obj.late_fee else '-'
    late_fee_display.short_description = _('Late Fee')


# =============================================================================
# SHOP INFORMATION ADMIN
# =============================================================================

@admin.register(ShopInformation)
class ShopInformationAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Business Information'), {
            'fields': ('shop_name', 'tagline', 'about_text', 'about_image_url')
        }),
        (_('Contact Information'), {
            'fields': (
                'phone_number', 'alternative_phone', 'whatsapp_number', 'email'
            )
        }),
        (_('Location'), {
            'fields': (
                'physical_address', 'district', 'landmark',
                'google_maps_link', 'google_maps_embed'
            )
        }),
        (_('Operating Hours'), {
            'fields': ('operating_hours',)
        }),
        (_('Social Media'), {
            'fields': (
                'facebook_page', 'instagram_handle', 'twitter_handle',
                'tiktok_handle', 'youtube_channel'
            ),
            'classes': ('collapse',)
        }),
        (_('Bank Details'), {
            'fields': (
                'bank_name', 'account_name', 'account_number', 'branch'
            ),
            'classes': ('collapse',)
        }),
        (_('Mobile Money'), {
            'fields': (
                'mtn_momo_name', 'mtn_momo_number',
                'airtel_money_name', 'airtel_money_number'
            ),
            'classes': ('collapse',)
        }),
        (_('Policies'), {
            'fields': (
                'return_policy', 'warranty_policy',
                'privacy_policy', 'terms_and_conditions'
            ),
            'classes': ('collapse',)
        }),
        (_('Branding & SEO'), {
            'fields': (
                'logo_url', 'favicon_url',
                'meta_description', 'meta_keywords'
            ),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )

    def has_add_permission(self, request):
        # Only one shop info instance allowed
        return not ShopInformation.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False


# =============================================================================
# PRODUCT COMPARISON ADMIN (Optional)
# =============================================================================

@admin.register(ProductComparison)
class ProductComparisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'product_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'session_id')
    readonly_fields = ('created_at', 'updated_at')

    def product_count(self, obj):
        return len(obj.product_ids)
    product_count.short_description = _('Products')
