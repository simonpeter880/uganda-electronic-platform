# Two-Factor Authentication (2FA) Setup Guide

This guide explains how to enable and use Two-Factor Authentication for admin users in the Uganda Electronics Platform.

## Overview

2FA adds an extra layer of security by requiring two forms of authentication:
1. **Something you know**: Password
2. **Something you have**: Time-based one-time password (TOTP) from authenticator app

## Installation

### 1. Install Dependencies

```bash
cd uganda-backend-code
pip install -r requirements-2fa.txt
```

This installs:
- `django-otp`: TOTP implementation
- `qrcode`: QR code generation
- `pyotp`: OTP utilities

### 2. Update Django Settings

Add to your `saleor/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
]

MIDDLEWARE = [
    # ... existing middleware
    'django_otp.middleware.OTPMiddleware',
    'uganda_backend_code.two_factor_auth.Require2FAMiddleware',  # Optional: Enforce 2FA for staff
]

# 2FA Settings
OTP_TOTP_ISSUER = 'Uganda Electronics'
OTP_LOGIN_URL = '/admin/login/'
```

### 3. Run Migrations

```bash
python manage.py migrate
```

This creates tables:
- `otp_totp_totpdevice`: Stores TOTP devices
- `otp_static_staticdevice`: Stores backup codes

### 4. Add GraphQL Schema

Add to your GraphQL schema (`uganda-backend-code/graphql/mutations.py`):

```python
from uganda_backend_code.two_factor_auth import TwoFactorAuthMutations

class Mutation(graphene.ObjectType):
    # ... existing mutations

    # 2FA Mutations
    enable_2fa = graphene.Field(
        Enable2FAOutput,
        description='Enable two-factor authentication'
    )

    confirm_2fa = graphene.Field(
        Confirm2FAOutput,
        token=graphene.String(required=True),
        description='Confirm 2FA setup with verification code'
    )

    disable_2fa = graphene.Field(
        Disable2FAOutput,
        token=graphene.String(required=True),
        description='Disable two-factor authentication'
    )

    verify_2fa_login = graphene.Field(
        Verify2FALoginOutput,
        email=graphene.String(required=True),
        password=graphene.String(required=True),
        token=graphene.String(required=True),
        description='Login with 2FA verification'
    )

    def resolve_enable_2fa(self, info):
        return TwoFactorAuthMutations.enable_2fa(self, info)

    def resolve_confirm_2fa(self, info, token):
        return TwoFactorAuthMutations.confirm_2fa(self, info, token)

    def resolve_disable_2fa(self, info, token):
        return TwoFactorAuthMutations.disable_2fa(self, info, token)

    def resolve_verify_2fa_login(self, info, email, password, token):
        return TwoFactorAuthMutations.verify_2fa_login(self, info, email, password, token)
```

## Usage

### For Admin Users

#### 1. Enable 2FA

**Via GraphQL:**

```graphql
mutation {
  enable2FA {
    qrCode
    secretKey
    backupCodes
    message
  }
}
```

Response includes:
- `qrCode`: Base64-encoded QR code image
- `secretKey`: Manual entry key (if QR scan doesn't work)
- `backupCodes`: Recovery codes (save these securely!)
- `message`: Setup instructions

#### 2. Set Up Authenticator App

**Compatible Apps:**
- Google Authenticator (iOS, Android)
- Microsoft Authenticator (iOS, Android)
- Authy (iOS, Android, Desktop)
- 1Password (with TOTP support)
- LastPass Authenticator

**Steps:**
1. Open your authenticator app
2. Scan the QR code from the mutation response
3. OR manually enter the secret key
4. App will generate a 6-digit code every 30 seconds

#### 3. Confirm 2FA Setup

```graphql
mutation {
  confirm2FA(token: "123456") {
    success
    message
  }
}
```

Replace `"123456"` with the code from your authenticator app.

**Important:** Save your backup codes! Store them securely (password manager, encrypted file).

#### 4. Login with 2FA

```graphql
mutation {
  verify2FALogin(
    email: "admin@example.com"
    password: "your_password"
    token: "123456"
  ) {
    success
    authToken
    message
  }
}
```

### For Developers

#### Check 2FA Status

```python
from uganda_backend_code.two_factor_auth import TwoFactorAuthService

user = User.objects.get(email='admin@example.com')
status = TwoFactorAuthService.get_2fa_status(user)

print(status)
# {
#   'enabled': True,
#   'device_name': 'admin@example.com-totp',
#   'created_at': datetime(...),
#   'last_used': 1234567890
# }
```

#### Verify Token Programmatically

```python
from uganda_backend_code.two_factor_auth import TwoFactorAuthService

user = User.objects.get(email='admin@example.com')
is_valid = TwoFactorAuthService.verify_2fa_token(user, '123456')

if is_valid:
    print('Token is valid')
else:
    print('Invalid token')
```

#### Disable 2FA (with token verification)

```graphql
mutation {
  disable2FA(token: "123456") {
    success
    message
  }
}
```

## Django Admin Integration

### Display 2FA Status

Add to your `UserAdmin`:

```python
from uganda_backend_code.two_factor_auth import TwoFactorAuthAdmin

class UserAdmin(TwoFactorAuthAdmin, admin.ModelAdmin):
    list_display = ['email', 'is_staff', 'get_2fa_status']

    actions = ['enable_2fa_action']
```

Now the user list shows 2FA status:
- ✅ Enabled
- ❌ Disabled

### Enforce 2FA for Staff

The `Require2FAMiddleware` automatically redirects staff users without 2FA to setup page.

To customize:

```python
# In settings.py
ENFORCE_2FA_FOR_STAFF = True  # Require all staff to use 2FA
ENFORCE_2FA_FOR_SUPERUSERS = True  # Require superusers to use 2FA
```

## Security Best Practices

### 1. Backup Codes

- Generate 8-10 backup codes during setup
- Store in password manager or encrypted file
- Each code is single-use
- Regenerate if running low

### 2. Recovery Process

If user loses authenticator device:

**Option 1: Use Backup Code**
```graphql
mutation {
  verify2FALogin(
    email: "admin@example.com"
    password: "password"
    token: "XXXX-YYYY"  # Backup code
  ) {
    success
    authToken
  }
}
```

**Option 2: Admin Assistance**
```python
# Admin can disable 2FA for user (in Django shell)
from uganda_backend_code.two_factor_auth import TwoFactorAuthService
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='admin@example.com')

# Verify identity first!
# Then disable 2FA (requires physical verification)
from django_otp.plugins.otp_totp.models import TOTPDevice
TOTPDevice.objects.filter(user=user).delete()
```

### 3. Token Validity

- TOTP tokens are valid for 30 seconds
- System allows ±1 time step (90 seconds total window)
- Prevents timing attacks
- Clock drift tolerance built-in

### 4. Rate Limiting

Add to prevent brute force:

```python
# In two_factor_auth.py
from django.core.cache import cache

def verify_2fa_token(user, token):
    cache_key = f'2fa_attempts_{user.id}'
    attempts = cache.get(cache_key, 0)

    if attempts >= 5:
        raise ValidationError('Too many failed attempts. Try again in 15 minutes.')

    device = TOTPDevice.objects.get(user=user, confirmed=True)

    if device.verify_token(token):
        cache.delete(cache_key)
        return True
    else:
        cache.set(cache_key, attempts + 1, 900)  # 15 minutes
        return False
```

## Testing

### Manual Testing

1. Create test user:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_user(
    email='test@example.com',
    password='testpass123',
    is_staff=True
)
```

2. Enable 2FA via GraphQL Playground
3. Scan QR code with authenticator
4. Confirm with generated code
5. Test login with 2FA

### Automated Testing

```python
# In tests/test_2fa.py
import pytest
from uganda_backend_code.two_factor_auth import TwoFactorAuthService

@pytest.mark.django_db
def test_enable_2fa(user):
    result = TwoFactorAuthService.enable_2fa(user)

    assert 'qr_code' in result
    assert 'secret_key' in result
    assert len(result['backup_codes']) == 8

@pytest.mark.django_db
def test_verify_token(user):
    # Enable 2FA
    result = TwoFactorAuthService.enable_2fa(user)

    # Generate valid token (in real test, use pyotp)
    import pyotp
    totp = pyotp.TOTP(result['secret_key'])
    token = totp.now()

    # Confirm setup
    TwoFactorAuthService.confirm_2fa(user, token)

    # Verify it works
    assert TwoFactorAuthService.verify_2fa_token(user, token)
```

## Troubleshooting

### "Invalid verification code" errors

**Causes:**
1. Time synchronization issue
2. Typing wrong code
3. Code expired (>30 seconds old)

**Solutions:**
1. Sync phone time with internet time
2. Double-check code from app
3. Generate fresh code

### QR Code not scanning

**Solutions:**
1. Use manual entry with secret key
2. Increase screen brightness
3. Try different authenticator app
4. Check QR code image quality

### Lost authenticator device

**Recovery:**
1. Use backup codes
2. Contact administrator for 2FA reset
3. Provide identity verification

### 2FA not enforcing for staff

**Check:**
1. Middleware is in MIDDLEWARE list
2. Middleware is after AuthenticationMiddleware
3. OTPMiddleware is installed
4. User is marked as `is_staff=True`

## Migration Guide

### Existing Users

To migrate existing admin users to 2FA:

```python
# migration_script.py
from django.contrib.auth import get_user_model
from uganda_backend_code.two_factor_auth import TwoFactorAuthService

User = get_user_model()

# Get all staff users
staff_users = User.objects.filter(is_staff=True)

for user in staff_users:
    if not TwoFactorAuthService.is_2fa_enabled(user):
        print(f'Send 2FA setup email to {user.email}')
        # Implement email notification
        # user.send_2fa_setup_email()
```

### Gradual Rollout

1. **Phase 1**: Optional 2FA (2 weeks)
   - Announce feature
   - Provide setup guides
   - Encourage adoption

2. **Phase 2**: Required for superusers (1 week)
   - Enforce for superusers only
   - Support during transition

3. **Phase 3**: Required for all staff
   - Enforce for all staff users
   - Provide recovery support

## API Reference

### TwoFactorAuthService

```python
TwoFactorAuthService.is_2fa_enabled(user) -> bool
TwoFactorAuthService.enable_2fa(user) -> dict
TwoFactorAuthService.confirm_2fa(user, token) -> bool
TwoFactorAuthService.verify_2fa_token(user, token) -> bool
TwoFactorAuthService.disable_2fa(user, token) -> bool
TwoFactorAuthService.get_2fa_status(user) -> dict
```

### GraphQL Mutations

```graphql
# Enable 2FA
mutation { enable2FA { qrCode secretKey backupCodes message } }

# Confirm setup
mutation { confirm2FA(token: "123456") { success message } }

# Disable 2FA
mutation { disable2FA(token: "123456") { success message } }

# Login with 2FA
mutation {
  verify2FALogin(email: "admin@example.com", password: "pass", token: "123456") {
    success authToken message
  }
}
```

## Support

For issues or questions:
- Check troubleshooting section
- Review server logs
- Contact technical support
- Consult Django OTP documentation: https://django-otp-official.readthedocs.io

## Security Disclosure

If you discover a security vulnerability in the 2FA implementation, please email security@uganda-electronics.ug (do not open public issue).
