# Uganda Electronics Platform - Database Migrations

This directory contains SQL migrations to transform Saleor into a Uganda-focused electronics e-commerce platform.

## Overview

These migrations add Uganda-specific features while removing unnecessary complexity for a single-merchant operation:

- **Currency**: Convert everything to UGX (Ugandan Shillings)
- **Payments**: Mobile Money (MTN, Airtel) + Cash payments
- **Delivery**: District-based delivery fees across Uganda
- **SMS**: Notification system via Africa's Talking
- **Electronics**: IMEI tracking, specifications, warranty management
- **Installments**: Popular payment method in Uganda
- **Shop Info**: Single shop configuration

## Migration Files

| File | Description |
|------|-------------|
| `001_currency_configuration.sql` | Set UGX as only currency, remove multi-currency support |
| `002_uganda_districts.sql` | Create Uganda districts table for delivery |
| `003_seed_uganda_districts.sql` | Seed all 135 Uganda districts with delivery fees |
| `004_mobile_money_payments.sql` | Mobile Money payment system (MTN, Airtel) |
| `005_uganda_delivery.sql` | Uganda delivery system with district-based fees |
| `006_sms_notifications.sql` | SMS notification system (Africa's Talking) |
| `007_electronics_features.sql` | IMEI tracking, specs, warranty, comparison |
| `008_installment_payments.sql` | Installment payment plans |
| `009_shop_information.sql` | Shop configuration (contact, hours, social media) |

## Prerequisites

1. **Backup your database first!**
   ```bash
   docker compose exec db pg_dump -U saleor saleor > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Ensure Saleor is running:**
   ```bash
   docker compose up -d
   ```

3. **Verify database connectivity:**
   ```bash
   docker compose exec db psql -U saleor -d saleor -c "SELECT version();"
   ```

## Running Migrations

### Option 1: Use the automated script (Recommended)

```bash
cd /home/cymo/project-two/saleor-platform
chmod +x migrations/uganda-platform/run_migrations.sh
./migrations/uganda-platform/run_migrations.sh
```

The script will:
- Check database connectivity
- Prompt for confirmation
- Run all migrations in order
- Report success/failure for each migration

### Option 2: Run manually

From the `saleor-platform` directory:

```bash
# Run each migration in order
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/001_currency_configuration.sql
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/002_uganda_districts.sql
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/003_seed_uganda_districts.sql
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/004_mobile_money_payments.sql
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/005_uganda_delivery.sql
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/006_sms_notifications.sql
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/007_electronics_features.sql
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/008_installment_payments.sql
docker compose exec -T db psql -U saleor -d saleor < migrations/uganda-platform/009_shop_information.sql
```

### Option 3: Run from within the database container

```bash
docker compose exec db bash
cd /docker-entrypoint-initdb.d  # Or wherever you mount the migrations
psql -U saleor -d saleor -f 001_currency_configuration.sql
# ... repeat for each file
```

## After Migration

### 1. Restart Saleor API
```bash
docker compose restart api worker
```

### 2. Verify the changes
```bash
docker compose exec db psql -U saleor -d saleor
```

Then run these checks:

```sql
-- Check currency
SELECT DISTINCT currency FROM order_order;
-- Should return only 'UGX'

-- Check districts
SELECT COUNT(*) FROM uganda_district;
-- Should return 135

-- Check new tables exist
\dt uganda_district
\dt payment_mobile_money_transaction
\dt order_delivery_uganda
\dt sms_notification
\dt product_serial_number
\dt order_installment_plan
\dt shop_information

-- Check shop info
SELECT * FROM shop_information;
```

### 3. Update Configuration

Update your `backend.env` or Django settings:

```python
# Currency
DEFAULT_CURRENCY = "UGX"
AVAILABLE_CURRENCIES = ["UGX"]

# Mobile Money API Credentials
MTN_MOMO_API_KEY = "your_mtn_api_key"
MTN_MOMO_USER_ID = "your_user_id"
MTN_MOMO_SUBSCRIPTION_KEY = "your_subscription_key"

AIRTEL_MONEY_CLIENT_ID = "your_airtel_client_id"
AIRTEL_MONEY_CLIENT_SECRET = "your_airtel_secret"

# SMS Configuration (Africa's Talking)
AFRICAS_TALKING_USERNAME = "sandbox"  # or your username
AFRICAS_TALKING_API_KEY = "your_api_key"
AFRICAS_TALKING_SENDER_ID = "YOUR_SHOP"

# Shop Configuration
SHOP_PHONE_NUMBER = "256700000000"
SHOP_EMAIL = "shop@yourstore.ug"
```

## What Changed?

### Currency & Pricing
- ✅ All prices converted to UGX
- ✅ Prices rounded to whole numbers (no cents)
- ✅ Single channel for Uganda
- ✅ 18% VAT configured

### Warehouse & Inventory
- ✅ Single warehouse (main shop)
- ✅ Simplified stock management
- ✅ Low stock alerts
- ✅ Supplier information on variants

### Shipping & Delivery
- ✅ 135 Uganda districts with delivery fees
- ✅ District-based delivery pricing
- ✅ Shop pickup option
- ✅ Landmark-based addresses

### Payments
- ✅ Mobile Money support (MTN, Airtel)
- ✅ Cash on delivery
- ✅ Cash in store
- ✅ Installment plans

### Electronics Features
- ✅ IMEI/Serial number tracking
- ✅ Product specifications (JSONB)
- ✅ Warranty tracking
- ✅ New vs Used condition
- ✅ Product comparison

### Notifications
- ✅ SMS via Africa's Talking
- ✅ Order confirmations
- ✅ Payment reminders
- ✅ Delivery updates

### Customer Data
- ✅ Phone numbers for Mobile Money
- ✅ Preferred language
- ✅ National ID for installments

## New Tables Created

1. **uganda_district** - 135 districts with delivery fees
2. **payment_mobile_money_transaction** - Mobile Money payments
3. **order_delivery_uganda** - Delivery details
4. **sms_notification** - SMS tracking
5. **product_serial_number** - IMEI/serial tracking
6. **product_comparison** - Compare products
7. **order_installment_plan** - Installment plans
8. **installment_payment** - Individual installments
9. **shop_information** - Shop config

## Extended Tables

### product_product
- warranty_months
- is_new
- condition
- imei_required

### product_productvariant
- specifications (JSONB)
- low_stock_threshold
- reorder_quantity
- supplier_name, supplier_phone, supplier_cost
- markup_percentage

### order_order
- payment_method
- payment_phone
- payment_verified
- verification_code
- customer_notified
- sms_sent

### account_user
- phone_number
- alternative_phone
- preferred_language

### account_address
- district_id
- sub_area
- landmark

## Rollback

If you need to rollback, restore from your backup:

```bash
# Stop containers
docker compose down

# Restore database
docker compose up -d db
cat backup_YYYYMMDD_HHMMSS.sql | docker compose exec -T db psql -U saleor -d saleor

# Restart everything
docker compose up -d
```

## Troubleshooting

### Migration fails on foreign key constraints
```sql
-- Check dependencies first
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f' AND confrelid::regclass::text LIKE '%table_name%';
```

### Duplicate key violations
```sql
-- Check for duplicates before migration
SELECT column_name, COUNT(*)
FROM table_name
GROUP BY column_name
HAVING COUNT(*) > 1;
```

### Cannot drop column
If Saleor code still references old columns, migrations may fail. In that case:
1. Update Django models first
2. Create and run Django migrations
3. Then run these SQL migrations

## Next Steps

1. **Create Django Models** - Mirror the new tables in Python
2. **Update GraphQL Schema** - Add queries/mutations for new features
3. **Integrate Mobile Money** - Implement MTN/Airtel API calls
4. **Set up SMS** - Configure Africa's Talking
5. **Update Frontend** - Add Uganda-specific UI components
6. **Test Payment Flow** - End-to-end testing with Mobile Money
7. **Configure Shop Info** - Update shop details via admin

## Support

For issues or questions:
- Check the main documentation: `/home/cymo/project-two/uganda-electronics-platform.md`
- Review Saleor docs: https://docs.saleor.io/
- Check migration logs for specific errors

## License

Same as Saleor platform - BSD-3-Clause
