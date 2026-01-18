"""
Celery Background Tasks for Uganda Platform
Schedule these tasks in Saleor's Celery configuration
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# PAYMENT TASKS
# =============================================================================

@shared_task(bind=True, max_retries=3)
def check_pending_mobile_money_payments(self):
    """
    Check status of pending Mobile Money payments
    Run every 5 minutes
    """
    from ..models import MobileMoneyTransaction
    from ..services.mobile_money import MobileMoneyService

    logger.info("Checking pending Mobile Money payments...")

    # Get pending transactions from last 24 hours
    cutoff_time = timezone.now() - timezone.timedelta(hours=24)
    pending_transactions = MobileMoneyTransaction.objects.filter(
        status='pending',
        initiated_at__gte=cutoff_time
    )

    momo_service = MobileMoneyService()
    checked_count = 0
    success_count = 0

    for transaction in pending_transactions:
        try:
            # Check status with provider
            is_paid = momo_service.verify_payment(
                transaction.provider,
                transaction.transaction_reference
            )

            if is_paid:
                transaction.status = 'successful'
                transaction.completed_at = timezone.now()
                transaction.save()

                # Update order
                order = transaction.order
                order.payment_verified = True
                order.payment_verified_at = timezone.now()
                order.save()

                success_count += 1

                # Send SMS confirmation
                send_payment_confirmed_sms.delay(transaction.id)

            checked_count += 1

        except Exception as e:
            logger.error(f"Error checking transaction {transaction.id}: {e}")
            continue

    logger.info(
        f"Checked {checked_count} transactions, {success_count} confirmed"
    )

    return {
        'checked': checked_count,
        'confirmed': success_count
    }


@shared_task
def send_payment_reminder_sms(order_id):
    """Send payment reminder SMS for unpaid order"""
    from ..models import SMSNotification
    from ..services.sms_service import SMSService
    from saleor.order.models import Order

    try:
        order = Order.objects.get(pk=order_id)

        if order.payment_verified:
            return "Order already paid"

        # Get customer phone
        phone = order.payment_phone or order.user.phone_number

        if not phone:
            return "No phone number found"

        # Send SMS
        sms_service = SMSService()
        result = sms_service.send_payment_reminder(
            phone_number=phone,
            order_number=str(order.number),
            amount_due=f"{order.total.gross.amount:,.0f}"
        )

        # Log SMS
        SMSNotification.objects.create(
            recipient_phone=phone,
            message=f"Payment reminder for order #{order.number}",
            notification_type='payment_reminder',
            order=order,
            status='sent' if result['success'] else 'failed',
            provider_message_id=result.get('message_id'),
            sent_at=timezone.now() if result['success'] else None
        )

        return f"Reminder sent to {phone}"

    except Exception as e:
        logger.error(f"Failed to send payment reminder: {e}")
        raise


@shared_task
def send_payment_confirmed_sms(transaction_id):
    """Send payment confirmation SMS"""
    from ..models import MobileMoneyTransaction, SMSNotification
    from ..services.sms_service import SMSService

    try:
        transaction = MobileMoneyTransaction.objects.get(pk=transaction_id)
        order = transaction.order

        phone = transaction.phone_number

        sms_service = SMSService()
        result = sms_service.send_payment_confirmation(
            phone_number=phone,
            order_number=str(order.number),
            amount=f"{transaction.amount:,.0f}"
        )

        SMSNotification.objects.create(
            recipient_phone=phone,
            message=f"Payment confirmed for order #{order.number}",
            notification_type='payment_confirmed',
            order=order,
            status='sent' if result['success'] else 'failed',
            provider_message_id=result.get('message_id'),
            sent_at=timezone.now() if result['success'] else None
        )

        return f"Confirmation sent to {phone}"

    except Exception as e:
        logger.error(f"Failed to send payment confirmation: {e}")
        raise


# =============================================================================
# INSTALLMENT TASKS
# =============================================================================

@shared_task
def check_overdue_installments():
    """
    Check for overdue installment payments
    Run daily at 9 AM
    """
    from ..models import InstallmentPayment, SMSNotification
    from ..services.sms_service import SMSService

    logger.info("Checking overdue installments...")

    today = timezone.now().date()

    # Get payments that are overdue
    overdue_payments = InstallmentPayment.objects.filter(
        status='pending',
        due_date__lt=today
    ).select_related('plan', 'plan__order')

    sms_service = SMSService()
    reminder_count = 0

    for payment in overdue_payments:
        # Update status to overdue
        payment.status = 'overdue'

        # Calculate late fee (e.g., 5% of amount due)
        days_overdue = (today - payment.due_date).days
        if days_overdue > 7:  # Apply late fee after 7 days
            late_fee = payment.amount_due * Decimal('0.05')
            payment.late_fee = late_fee

        payment.save()

        # Send reminder SMS
        try:
            order = payment.plan.order
            phone = order.user.phone_number

            if phone:
                result = sms_service.send_installment_reminder(
                    phone_number=phone,
                    order_number=str(order.number),
                    installment_number=payment.installment_number,
                    amount_due=f"{payment.amount_due + payment.late_fee:,.0f}",
                    due_date=payment.due_date.strftime('%d %b %Y')
                )

                if result['success']:
                    reminder_count += 1

                    SMSNotification.objects.create(
                        recipient_phone=phone,
                        message=f"Overdue installment reminder",
                        notification_type='installment_reminder',
                        order=order,
                        status='sent',
                        provider_message_id=result.get('message_id'),
                        sent_at=timezone.now()
                    )

        except Exception as e:
            logger.error(f"Failed to send reminder for payment {payment.id}: {e}")
            continue

    logger.info(f"Sent {reminder_count} overdue reminders")
    return {'reminders_sent': reminder_count}


@shared_task
def send_upcoming_installment_reminders():
    """
    Send reminders for installments due in 3 days
    Run daily at 10 AM
    """
    from ..models import InstallmentPayment, SMSNotification
    from ..services.sms_service import SMSService

    logger.info("Sending upcoming installment reminders...")

    # Get payments due in 3 days
    reminder_date = timezone.now().date() + timezone.timedelta(days=3)

    upcoming_payments = InstallmentPayment.objects.filter(
        status='pending',
        due_date=reminder_date
    ).select_related('plan', 'plan__order')

    sms_service = SMSService()
    reminder_count = 0

    for payment in upcoming_payments:
        try:
            order = payment.plan.order
            phone = order.user.phone_number

            if phone:
                result = sms_service.send_installment_reminder(
                    phone_number=phone,
                    order_number=str(order.number),
                    installment_number=payment.installment_number,
                    amount_due=f"{payment.amount_due:,.0f}",
                    due_date=payment.due_date.strftime('%d %b %Y')
                )

                if result['success']:
                    reminder_count += 1

                    SMSNotification.objects.create(
                        recipient_phone=phone,
                        message=f"Installment payment reminder",
                        notification_type='installment_reminder',
                        order=order,
                        status='sent',
                        provider_message_id=result.get('message_id'),
                        sent_at=timezone.now()
                    )

        except Exception as e:
            logger.error(f"Failed to send reminder for payment {payment.id}: {e}")
            continue

    logger.info(f"Sent {reminder_count} upcoming payment reminders")
    return {'reminders_sent': reminder_count}


# =============================================================================
# INVENTORY TASKS
# =============================================================================

@shared_task
def check_low_stock_items():
    """
    Check for products with low stock and send alerts
    Run daily at 8 AM
    """
    from saleor.product.models import ProductVariant
    from saleor.warehouse.models import Stock

    logger.info("Checking low stock items...")

    low_stock_items = []

    # Get all variants with low stock threshold
    variants = ProductVariant.objects.filter(
        low_stock_threshold__isnull=False
    ).prefetch_related('stocks')

    for variant in variants:
        total_stock = sum(stock.quantity for stock in variant.stocks.all())

        if total_stock <= variant.low_stock_threshold:
            low_stock_items.append({
                'variant_id': variant.id,
                'sku': variant.sku,
                'name': variant.name,
                'current_stock': total_stock,
                'threshold': variant.low_stock_threshold,
                'suggested_reorder': variant.reorder_quantity or 20
            })

    # TODO: Send email/SMS to staff about low stock items
    if low_stock_items:
        logger.warning(f"Found {len(low_stock_items)} low stock items")

    return {'low_stock_count': len(low_stock_items), 'items': low_stock_items}


@shared_task
def check_expired_serial_warranties():
    """
    Check for products with expiring warranties
    Run daily
    """
    from ..models import ProductSerialNumber

    logger.info("Checking expiring warranties...")

    # Get serial numbers with warranties expiring in 7 days
    expiry_date = timezone.now().date() + timezone.timedelta(days=7)

    expiring_warranties = ProductSerialNumber.objects.filter(
        status='sold',
        warranty_expires_at=expiry_date
    ).select_related('sold_in_order')

    # TODO: Send notifications to customers about expiring warranties

    logger.info(f"Found {expiring_warranties.count()} expiring warranties")
    return {'expiring_count': expiring_warranties.count()}


# =============================================================================
# SMS RETRY TASKS
# =============================================================================

@shared_task(bind=True, max_retries=3)
def retry_failed_sms(self, sms_id):
    """Retry sending failed SMS"""
    from ..models import SMSNotification
    from ..services.sms_service import SMSService

    try:
        sms = SMSNotification.objects.get(pk=sms_id)

        if sms.retry_count >= sms.max_retries:
            logger.error(f"SMS {sms_id} exceeded max retries")
            return "Max retries exceeded"

        sms_service = SMSService()
        result = sms_service.send_single_sms(
            phone_number=sms.recipient_phone,
            message=sms.message
        )

        if result['success']:
            sms.status = 'sent'
            sms.sent_at = timezone.now()
            sms.provider_message_id = result.get('message_id')
            sms.error_message = ''
        else:
            sms.retry_count += 1
            sms.error_message = f"Retry {sms.retry_count} failed"

        sms.save()

        return f"Retry {'successful' if result['success'] else 'failed'}"

    except Exception as e:
        logger.error(f"Error retrying SMS {sms_id}: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


# =============================================================================
# CLEANUP TASKS
# =============================================================================

@shared_task
def cleanup_old_sms_notifications():
    """
    Delete SMS notifications older than 90 days
    Run weekly
    """
    from ..models import SMSNotification

    cutoff_date = timezone.now() - timezone.timedelta(days=90)

    deleted_count, _ = SMSNotification.objects.filter(
        created_at__lt=cutoff_date
    ).delete()

    logger.info(f"Deleted {deleted_count} old SMS notifications")
    return {'deleted_count': deleted_count}


@shared_task
def cleanup_old_comparisons():
    """
    Delete product comparisons older than 30 days
    Run weekly
    """
    from ..models import ProductComparison

    cutoff_date = timezone.now() - timezone.timedelta(days=30)

    deleted_count, _ = ProductComparison.objects.filter(
        user__isnull=True,  # Only anonymous comparisons
        created_at__lt=cutoff_date
    ).delete()

    logger.info(f"Deleted {deleted_count} old product comparisons")
    return {'deleted_count': deleted_count}


# =============================================================================
# CELERY BEAT SCHEDULE
# Add this to your Saleor settings.py or celery configuration
# =============================================================================

"""
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Check pending Mobile Money payments every 5 minutes
    'check-pending-mobile-money-payments': {
        'task': 'uganda.tasks.check_pending_mobile_money_payments',
        'schedule': crontab(minute='*/5'),
    },

    # Check overdue installments daily at 9 AM
    'check-overdue-installments': {
        'task': 'uganda.tasks.check_overdue_installments',
        'schedule': crontab(hour=9, minute=0),
    },

    # Send upcoming installment reminders daily at 10 AM
    'send-upcoming-installment-reminders': {
        'task': 'uganda.tasks.send_upcoming_installment_reminders',
        'schedule': crontab(hour=10, minute=0),
    },

    # Check low stock daily at 8 AM
    'check-low-stock-items': {
        'task': 'uganda.tasks.check_low_stock_items',
        'schedule': crontab(hour=8, minute=0),
    },

    # Check expiring warranties daily at 11 AM
    'check-expired-warranties': {
        'task': 'uganda.tasks.check_expired_serial_warranties',
        'schedule': crontab(hour=11, minute=0),
    },

    # Cleanup old SMS weekly on Sunday at midnight
    'cleanup-old-sms': {
        'task': 'uganda.tasks.cleanup_old_sms_notifications',
        'schedule': crontab(hour=0, minute=0, day_of_week=0),
    },

    # Cleanup old comparisons weekly on Sunday at 1 AM
    'cleanup-old-comparisons': {
        'task': 'uganda.tasks.cleanup_old_comparisons',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),
    },
}
"""
