# 🚀 Uganda Electronics Platform - Quick Start Guide

**5-minute setup to get your platform running**

## ⚡ Step 1: Run Migrations (2 minutes)

```bash
cd /home/cymo/project-two/saleor-platform
./migrations/uganda-platform/run_migrations.sh
```

Type `yes` when prompted.

**What this does:**
- ✅ Sets currency to UGX
- ✅ Adds 135 Uganda districts
- ✅ Creates Mobile Money payment tables
- ✅ Adds SMS notification system
- ✅ Adds IMEI tracking for electronics

---

## ⚡ Step 2: Restart Services (30 seconds)

```bash
docker compose restart api worker
```

---

## ⚡ Step 3: Configure APIs (2 minutes)

Edit `backend.env`:

```bash
# MTN Mobile Money (Get from: momodeveloper.mtn.com)
MTN_MOMO_API_USER=your_user_id
MTN_MOMO_API_KEY=your_api_key
MTN_MOMO_SUBSCRIPTION_KEY=your_subscription_key

# Airtel Money (Contact Airtel Uganda)
AIRTEL_MONEY_CLIENT_ID=your_client_id
AIRTEL_MONEY_CLIENT_SECRET=your_client_secret

# Africa's Talking SMS (Get from: africastalking.com)
AFRICAS_TALKING_USERNAME=sandbox  # Change to your username when live
AFRICAS_TALKING_API_KEY=your_api_key
AFRICAS_TALKING_SENDER_ID=YOURSHOP

# Your Shop Details
SHOP_PHONE=256700000000
SHOP_EMAIL=shop@yourstore.ug
```

---

## ⚡ Step 4: Test (1 minute)

### Test Database

```bash
docker compose exec db psql -U saleor -d saleor -c "SELECT COUNT(*) FROM uganda_district;"
```

Should return: 135

### Check Currency

```bash
docker compose exec db psql -U saleor -d saleor -c "SELECT DISTINCT currency FROM channel_channel;"
```

Should return: UGX

---

## 🎯 What You Can Do Now

### 1. View Districts & Delivery Fees

```bash
docker compose exec db psql -U saleor -d saleor -c "
SELECT name, region, delivery_fee, estimated_delivery_days
FROM uganda_district
ORDER BY delivery_fee
LIMIT 10;
"
```

### 2. Update Shop Information

```bash
docker compose exec api python manage.py shell
```

```python
from models import ShopInformation
shop = ShopInformation.objects.get(id=1)
shop.shop_name = "Your Shop Name"
shop.phone_number = "256700123456"
shop.physical_address = "Kampala, Uganda"
shop.save()
print("✓ Shop updated!")
```

### 3. Test Mobile Money (Sandbox)

```python
from services.mobile_money import MobileMoneyService
from decimal import Decimal

momo = MobileMoneyService()
tx_id, resp = momo.initiate_payment(
    provider='mtn_momo',
    phone_number='256700123456',
    amount=Decimal('5000'),
    order_number='TEST-001'
)
print(f"Payment initiated: {tx_id}")
```

### 4. Test SMS (Sandbox)

```python
from services.sms_service import SMSService

sms = SMSService()
result = sms.send_order_confirmation(
    phone_number='256700123456',
    order_number='TEST-001',
    total_amount='50,000'
)
print(f"SMS sent: {result['success']}")
```

---

## 📱 Common Commands

### View Logs
```bash
docker compose logs -f api
```

### Access Database
```bash
docker compose exec db psql -U saleor -d saleor
```

### Django Shell
```bash
docker compose exec api python manage.py shell
```

### Restart Everything
```bash
docker compose restart
```

---

## 🆘 Quick Fixes

### "Migration failed"
```bash
# Check database is running
docker compose ps

# Restart database
docker compose restart db

# Try migration again
./migrations/uganda-platform/run_migrations.sh
```

### "Can't connect to database"
```bash
# Start services
docker compose up -d

# Wait 30 seconds, then try again
```

### "API not responding"
```bash
# Check API logs
docker compose logs api

# Restart API
docker compose restart api
```

---

## 📚 Next Steps

1. **Read full docs**: [UGANDA_PLATFORM_SETUP.md](UGANDA_PLATFORM_SETUP.md)
2. **Get API keys**:
   - MTN MoMo: https://momodeveloper.mtn.com/
   - Africa's Talking: https://africastalking.com/
3. **Add products** via Saleor admin: http://localhost:8000/graphql/
4. **Test orders** end-to-end
5. **Update frontend** with Uganda features

---

## 💡 Pro Tips

- Start with **sandbox/test mode** for all APIs
- Test payments with **small amounts** (UGX 1,000-5,000)
- Use your **own phone number** for SMS testing
- Check **SMS credits** regularly on Africa's Talking
- Monitor **transaction fees** on Mobile Money
- **Backup database** before any changes:
  ```bash
  docker compose exec db pg_dump -U saleor saleor > backup.sql
  ```

---

## ✅ You're Ready!

Your Uganda electronics platform is now set up with:

- ✅ UGX currency
- ✅ 135 districts with delivery fees
- ✅ Mobile Money (MTN, Airtel)
- ✅ SMS notifications
- ✅ IMEI tracking
- ✅ Installment payments
- ✅ Shop configuration

**Happy selling! 🎉**

For detailed documentation, see [README.md](README.md) or [UGANDA_PLATFORM_SETUP.md](UGANDA_PLATFORM_SETUP.md)
