"""
Django models for Uganda Electronics Platform
These models should be added to your Saleor installation
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _


# ============================================================================
# UGANDA DISTRICTS & DELIVERY
# ============================================================================

class UgandaDistrict(models.Model):
    """Uganda districts for delivery fee calculation"""

    REGION_CHOICES = [
        ('Central', _('Central Region')),
        ('Eastern', _('Eastern Region')),
        ('Northern', _('Northern Region')),
        ('Western', _('Western Region')),
    ]

    name = models.CharField(max_length=100, unique=True, db_index=True)
    region = models.CharField(max_length=50, choices=REGION_CHOICES, db_index=True)

    # Delivery configuration
    delivery_available = models.BooleanField(default=True)
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Delivery fee in UGX")
    )
    estimated_delivery_days = models.PositiveIntegerField(default=3)

    # Popular sub-areas within district
    sub_areas = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text=_("Popular areas within the district")
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'uganda_district'
        verbose_name = _('Uganda District')
        verbose_name_plural = _('Uganda Districts')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['region']),
            models.Index(fields=['delivery_available']),
        ]

    def __str__(self):
        return f"{self.name} ({self.region})"


class OrderDeliveryUganda(models.Model):
    """Delivery details for orders in Uganda"""

    DELIVERY_METHOD_CHOICES = [
        ('shop_pickup', _('Shop Pickup')),
        ('home_delivery', _('Home Delivery')),
        ('office_delivery', _('Office Delivery')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('ready_for_pickup', _('Ready for Pickup')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('failed', _('Delivery Failed')),
    ]

    # Phone number validator for Uganda (256XXXXXXXXX)
    phone_validator = RegexValidator(
        regex=r'^256[0-9]{9}$',
        message=_('Phone number must be in format: 256XXXXXXXXX')
    )

    order = models.OneToOneField(
        'order.Order',
        on_delete=models.CASCADE,
        related_name='uganda_delivery'
    )

    # Location
    district = models.ForeignKey(
        UgandaDistrict,
        on_delete=models.PROTECT,
        related_name='deliveries'
    )
    sub_area = models.CharField(max_length=255, blank=True)
    street_address = models.TextField()
    landmark = models.TextField(
        blank=True,
        help_text=_('e.g., "Near Shell Ntinda", "Opposite Shoprite"')
    )

    # Recipient
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(
        max_length=15,
        validators=[phone_validator]
    )
    alternative_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[phone_validator]
    )

    # Delivery preferences
    delivery_method = models.CharField(
        max_length=50,
        choices=DELIVERY_METHOD_CHOICES
    )
    delivery_instructions = models.TextField(blank=True)

    # Pickup details
    pickup_ready_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)

    # Delivery details
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    estimated_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)

    # Delivery person
    delivered_by_name = models.CharField(max_length=255, blank=True)
    delivered_by_phone = models.CharField(max_length=15, blank=True)

    # Status
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    delivery_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_delivery_uganda'
        verbose_name = _('Uganda Delivery')
        verbose_name_plural = _('Uganda Deliveries')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['estimated_delivery_date']),
            models.Index(fields=['recipient_phone']),
        ]

    def __str__(self):
        return f"Delivery for Order #{self.order.number}"


# ============================================================================
# MOBILE MONEY PAYMENTS
# ============================================================================

class MobileMoneyTransaction(models.Model):
    """Mobile Money payment transactions (MTN, Airtel)"""

    PROVIDER_CHOICES = [
        ('mtn_momo', _('MTN Mobile Money')),
        ('airtel_money', _('Airtel Money')),
        ('cash', _('Cash')),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('mobile_money', _('Mobile Money')),
        ('cash_on_delivery', _('Cash on Delivery')),
        ('cash_in_store', _('Cash in Store')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('successful', _('Successful')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]

    phone_validator = RegexValidator(
        regex=r'^256[0-9]{9}$',
        message=_('Phone number must be in format: 256XXXXXXXXX')
    )

    order = models.ForeignKey(
        'order.Order',
        on_delete=models.CASCADE,
        related_name='momo_transactions'
    )

    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    phone_number = models.CharField(
        max_length=15,
        validators=[phone_validator],
        blank=True
    )
    transaction_reference = models.CharField(
        max_length=255,
        blank=True,
        db_index=True
    )

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3, default='UGX')

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES
    )

    # Verification
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    verified_by_staff = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    # Provider response
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_mobile_money_transaction'
        verbose_name = _('Mobile Money Transaction')
        verbose_name_plural = _('Mobile Money Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['provider']),
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return f"{self.get_provider_display()} - {self.amount} UGX - {self.get_status_display()}"


# ============================================================================
# SMS NOTIFICATIONS
# ============================================================================

class SMSNotification(models.Model):
    """SMS notifications sent via Africa's Talking"""

    NOTIFICATION_TYPE_CHOICES = [
        ('order_confirmation', _('Order Confirmation')),
        ('payment_reminder', _('Payment Reminder')),
        ('payment_confirmed', _('Payment Confirmed')),
        ('ready_for_pickup', _('Ready for Pickup')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('delivery_failed', _('Delivery Failed')),
        ('installment_reminder', _('Installment Payment Reminder')),
        ('general', _('General')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed')),
    ]

    phone_validator = RegexValidator(
        regex=r'^256[0-9]{9}$',
        message=_('Phone number must be in format: 256XXXXXXXXX')
    )

    recipient_phone = models.CharField(
        max_length=15,
        validators=[phone_validator],
        db_index=True
    )
    message = models.TextField()

    notification_type = models.CharField(
        max_length=100,
        choices=NOTIFICATION_TYPE_CHOICES,
        db_index=True
    )
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sms_notifications'
    )
    user = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sms_notifications'
    )

    provider = models.CharField(max_length=50, default='africas_talking')

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    provider_message_id = models.CharField(max_length=255, blank=True, db_index=True)
    provider_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    cost = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Cost in UGX")
    )

    # Retry logic
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sms_notification'
        verbose_name = _('SMS Notification')
        verbose_name_plural = _('SMS Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['recipient_phone']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"SMS to {self.recipient_phone} - {self.get_notification_type_display()}"


# ============================================================================
# ELECTRONICS FEATURES
# ============================================================================

class ProductSerialNumber(models.Model):
    """Track IMEI/Serial numbers for electronics"""

    SERIAL_TYPE_CHOICES = [
        ('imei', _('IMEI')),
        ('serial', _('Serial Number')),
        ('mac_address', _('MAC Address')),
    ]

    STATUS_CHOICES = [
        ('in_stock', _('In Stock')),
        ('sold', _('Sold')),
        ('reserved', _('Reserved')),
        ('returned', _('Returned')),
        ('defective', _('Defective')),
    ]

    variant = models.ForeignKey(
        'product.ProductVariant',
        on_delete=models.CASCADE,
        related_name='serial_numbers'
    )

    serial_number = models.CharField(max_length=255, unique=True, db_index=True)
    serial_type = models.CharField(max_length=50, choices=SERIAL_TYPE_CHOICES)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='in_stock',
        db_index=True
    )

    # Tracking
    purchase_date = models.DateField(null=True, blank=True)
    sold_in_order = models.ForeignKey(
        'order.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='serial_numbers'
    )
    sold_date = models.DateField(null=True, blank=True)

    # Warranty
    warranty_expires_at = models.DateField(null=True, blank=True, db_index=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_serial_number'
        verbose_name = _('Product Serial Number')
        verbose_name_plural = _('Product Serial Numbers')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
            models.Index(fields=['warranty_expires_at']),
        ]

    def __str__(self):
        return f"{self.get_serial_type_display()}: {self.serial_number}"


class ProductComparison(models.Model):
    """User product comparison lists"""

    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(
        'account.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='product_comparisons'
    )
    session_id = models.CharField(max_length=255, blank=True, db_index=True)

    product_ids = ArrayField(
        models.IntegerField(),
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_comparison'
        verbose_name = _('Product Comparison')
        verbose_name_plural = _('Product Comparisons')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else f"Session {self.session_id}"
        return f"Comparison by {user_str}"


# ============================================================================
# INSTALLMENT PAYMENTS
# ============================================================================

class InstallmentPlan(models.Model):
    """Installment payment plans for orders"""

    FREQUENCY_CHOICES = [
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
    ]

    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('defaulted', _('Defaulted')),
        ('cancelled', _('Cancelled')),
    ]

    order = models.OneToOneField(
        'order.Order',
        on_delete=models.CASCADE,
        related_name='installment_plan'
    )

    # Plan details
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    down_payment = models.DecimalField(max_digits=20, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=20, decimal_places=2)

    installment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    number_of_installments = models.PositiveIntegerField()
    installment_frequency = models.CharField(
        max_length=50,
        choices=FREQUENCY_CHOICES,
        default='monthly'
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )

    # Tracking
    paid_installments = models.PositiveIntegerField(default=0)
    next_payment_due_date = models.DateField(db_index=True)

    # Interest
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Customer verification
    customer_national_id = models.CharField(max_length=50, blank=True)
    customer_id_photo_url = models.URLField(max_length=500, blank=True)
    guarantor_name = models.CharField(max_length=255, blank=True)
    guarantor_phone = models.CharField(max_length=15, blank=True)
    guarantor_relationship = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_installment_plan'
        verbose_name = _('Installment Plan')
        verbose_name_plural = _('Installment Plans')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['next_payment_due_date']),
            models.Index(fields=['customer_national_id']),
        ]

    def __str__(self):
        return f"Installment Plan for Order #{self.order.number}"


class InstallmentPayment(models.Model):
    """Individual installment payments"""

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('waived', _('Waived')),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('mtn_momo', _('MTN Mobile Money')),
        ('airtel_money', _('Airtel Money')),
        ('cash', _('Cash')),
    ]

    plan = models.ForeignKey(
        InstallmentPlan,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    installment_number = models.PositiveIntegerField()

    amount_due = models.DecimalField(max_digits=20, decimal_places=2)
    amount_paid = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )

    due_date = models.DateField(db_index=True)
    paid_date = models.DateField(null=True, blank=True)

    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True
    )
    payment_reference = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )

    late_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'installment_payment'
        verbose_name = _('Installment Payment')
        verbose_name_plural = _('Installment Payments')
        ordering = ['plan', 'installment_number']
        unique_together = [['plan', 'installment_number']]
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['installment_number']),
        ]

    def __str__(self):
        return f"Payment {self.installment_number}/{self.plan.number_of_installments} for Order #{self.plan.order.number}"


# ============================================================================
# SHOP INFORMATION
# ============================================================================

class ShopInformation(models.Model):
    """Shop configuration and contact information (single row)"""

    # Business details
    shop_name = models.CharField(max_length=255, default='Electronics Shop Uganda')
    tagline = models.CharField(max_length=500, blank=True)

    # Contact
    phone_number = models.CharField(max_length=15)
    alternative_phone = models.CharField(max_length=15, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField()

    # Location
    physical_address = models.TextField()
    district = models.ForeignKey(
        UgandaDistrict,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    landmark = models.TextField(blank=True)
    google_maps_link = models.URLField(max_length=1000, blank=True)
    google_maps_embed = models.TextField(blank=True)

    # Operating hours
    operating_hours = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Operating hours in JSON format')
    )

    # Social media
    facebook_page = models.URLField(max_length=500, blank=True)
    instagram_handle = models.CharField(max_length=100, blank=True)
    twitter_handle = models.CharField(max_length=100, blank=True)
    tiktok_handle = models.CharField(max_length=100, blank=True)
    youtube_channel = models.URLField(max_length=500, blank=True)

    # Policies
    return_policy = models.TextField(blank=True)
    warranty_policy = models.TextField(blank=True)
    privacy_policy = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)

    # Bank details
    bank_name = models.CharField(max_length=255, blank=True)
    account_name = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    branch = models.CharField(max_length=255, blank=True)

    # Mobile Money
    mtn_momo_name = models.CharField(max_length=255, blank=True)
    mtn_momo_number = models.CharField(max_length=15, blank=True)
    airtel_money_name = models.CharField(max_length=255, blank=True)
    airtel_money_number = models.CharField(max_length=15, blank=True)

    # About
    about_text = models.TextField(blank=True)
    about_image_url = models.URLField(max_length=500, blank=True)

    # Branding
    logo_url = models.URLField(max_length=500, blank=True)
    favicon_url = models.URLField(max_length=500, blank=True)

    # SEO
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shop_information'
        verbose_name = _('Shop Information')
        verbose_name_plural = _('Shop Information')

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and ShopInformation.objects.exists():
            raise ValueError(_('Only one Shop Information instance is allowed'))
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.shop_name
