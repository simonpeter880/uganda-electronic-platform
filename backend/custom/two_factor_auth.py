"""
Two-Factor Authentication (2FA) implementation for Uganda Electronics Platform
Using TOTP (Time-based One-Time Password) with django-otp
"""
import os
import qrcode
import io
import base64
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

User = get_user_model()


class TwoFactorAuthService:
    """
    Service for managing two-factor authentication
    """

    @staticmethod
    def is_2fa_enabled(user):
        """
        Check if 2FA is enabled for a user

        Args:
            user: User instance

        Returns:
            bool: True if 2FA is enabled and confirmed
        """
        return TOTPDevice.objects.filter(
            user=user,
            confirmed=True
        ).exists()

    @staticmethod
    def enable_2fa(user):
        """
        Enable 2FA for a user and generate a new device

        Args:
            user: User instance

        Returns:
            dict: Contains device info and QR code data
        """
        # Check if already enabled
        if TwoFactorAuthService.is_2fa_enabled(user):
            raise ValidationError('2FA is already enabled for this user')

        # Delete any unconfirmed devices
        TOTPDevice.objects.filter(user=user, confirmed=False).delete()

        # Create new TOTP device
        device = TOTPDevice.objects.create(
            user=user,
            name=f'{user.email}-totp',
            confirmed=False,
            key=random_hex(20)  # Generate random secret key
        )

        # Generate provisioning URI
        provisioning_uri = device.config_url

        # Generate QR code
        qr_code_data = TwoFactorAuthService._generate_qr_code(provisioning_uri)

        return {
            'device_id': device.id,
            'secret_key': device.key,
            'qr_code': qr_code_data,
            'provisioning_uri': provisioning_uri,
            'backup_codes': TwoFactorAuthService._generate_backup_codes(user)
        }

    @staticmethod
    def confirm_2fa(user, token):
        """
        Confirm 2FA setup by verifying the first token

        Args:
            user: User instance
            token: 6-digit TOTP token

        Returns:
            bool: True if token is valid and 2FA is confirmed
        """
        # Get unconfirmed device
        try:
            device = TOTPDevice.objects.get(user=user, confirmed=False)
        except TOTPDevice.DoesNotExist:
            raise ValidationError('No pending 2FA setup found')

        # Verify token
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            return True
        else:
            raise ValidationError('Invalid verification code')

    @staticmethod
    def verify_2fa_token(user, token):
        """
        Verify a 2FA token for login

        Args:
            user: User instance
            token: 6-digit TOTP token

        Returns:
            bool: True if token is valid
        """
        # Get confirmed device
        try:
            device = TOTPDevice.objects.get(user=user, confirmed=True)
        except TOTPDevice.DoesNotExist:
            return False

        return device.verify_token(token)

    @staticmethod
    def disable_2fa(user, token):
        """
        Disable 2FA for a user (requires valid token)

        Args:
            user: User instance
            token: 6-digit TOTP token for verification

        Returns:
            bool: True if successfully disabled
        """
        # Verify token before disabling
        if not TwoFactorAuthService.verify_2fa_token(user, token):
            raise ValidationError('Invalid verification code')

        # Delete all TOTP devices for this user
        TOTPDevice.objects.filter(user=user).delete()

        return True

    @staticmethod
    def _generate_qr_code(provisioning_uri):
        """
        Generate QR code for TOTP setup

        Args:
            provisioning_uri: TOTP provisioning URI

        Returns:
            str: Base64-encoded QR code image
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f'data:image/png;base64,{img_str}'

    @staticmethod
    def _generate_backup_codes(user, count=8):
        """
        Generate backup codes for account recovery

        Args:
            user: User instance
            count: Number of backup codes to generate

        Returns:
            list: List of backup codes
        """
        # You can store these in a separate model or encrypted field
        # For now, returning generated codes
        backup_codes = [
            f'{random_hex(4)}-{random_hex(4)}'.upper()
            for _ in range(count)
        ]

        return backup_codes

    @staticmethod
    def get_2fa_status(user):
        """
        Get detailed 2FA status for a user

        Args:
            user: User instance

        Returns:
            dict: 2FA status information
        """
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        return {
            'enabled': device is not None,
            'device_name': device.name if device else None,
            'created_at': device.created_at if device else None,
            'last_used': device.last_t if device else None,
        }


# GraphQL Types and Mutations for 2FA

class TwoFactorAuthTypes:
    """
    GraphQL type definitions for 2FA
    """

    @staticmethod
    def enable_2fa_type():
        """
        Return type for enable2FA mutation

        {
          "qrCode": "data:image/png;base64,...",
          "secretKey": "ABCD1234...",
          "backupCodes": ["XXXX-YYYY", ...],
          "message": "Scan QR code with authenticator app"
        }
        """
        pass

    @staticmethod
    def verify_2fa_type():
        """
        Return type for verify2FA mutation

        {
          "success": true,
          "message": "2FA enabled successfully"
        }
        """
        pass


class TwoFactorAuthMutations:
    """
    GraphQL mutations for 2FA
    """

    @staticmethod
    def enable_2fa(root, info):
        """
        Mutation: enable2FA

        Enables 2FA for the authenticated user and returns QR code

        Example:
        mutation {
          enable2FA {
            qrCode
            secretKey
            backupCodes
            message
          }
        }
        """
        user = info.context.user

        if not user.is_authenticated:
            raise ValidationError('Authentication required')

        result = TwoFactorAuthService.enable_2fa(user)

        return {
            'qr_code': result['qr_code'],
            'secret_key': result['secret_key'],
            'backup_codes': result['backup_codes'],
            'message': 'Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)'
        }

    @staticmethod
    def confirm_2fa(root, info, token):
        """
        Mutation: confirm2FA

        Confirms 2FA setup with the first token

        Args:
            token: 6-digit TOTP token

        Example:
        mutation {
          confirm2FA(token: "123456") {
            success
            message
          }
        }
        """
        user = info.context.user

        if not user.is_authenticated:
            raise ValidationError('Authentication required')

        TwoFactorAuthService.confirm_2fa(user, token)

        return {
            'success': True,
            'message': '2FA has been enabled successfully. Save your backup codes in a secure location.'
        }

    @staticmethod
    def disable_2fa(root, info, token):
        """
        Mutation: disable2FA

        Disables 2FA for the user

        Args:
            token: 6-digit TOTP token for verification

        Example:
        mutation {
          disable2FA(token: "123456") {
            success
            message
          }
        }
        """
        user = info.context.user

        if not user.is_authenticated:
            raise ValidationError('Authentication required')

        TwoFactorAuthService.disable_2fa(user, token)

        return {
            'success': True,
            'message': '2FA has been disabled'
        }

    @staticmethod
    def verify_2fa_login(root, info, email, password, token):
        """
        Mutation: verify2FALogin

        Login with 2FA verification

        Args:
            email: User email
            password: User password
            token: 6-digit TOTP token

        Example:
        mutation {
          verify2FALogin(
            email: "admin@example.com"
            password: "password123"
            token: "123456"
          ) {
            success
            authToken
            message
          }
        }
        """
        from django.contrib.auth import authenticate

        # Authenticate with password
        user = authenticate(email=email, password=password)

        if not user:
            raise ValidationError('Invalid credentials')

        # Check if 2FA is enabled
        if not TwoFactorAuthService.is_2fa_enabled(user):
            raise ValidationError('2FA is not enabled for this user')

        # Verify 2FA token
        if not TwoFactorAuthService.verify_2fa_token(user, token):
            raise ValidationError('Invalid 2FA code')

        # Generate auth token (implement according to your auth system)
        # This is a placeholder - replace with actual token generation
        from saleor.graphql.account.mutations.authentication import CreateToken
        token_result = CreateToken.perform_mutation(root, info, email=email, password=password)

        return {
            'success': True,
            'auth_token': token_result.token,
            'message': 'Login successful'
        }


# Django Admin Integration

class TwoFactorAuthAdmin:
    """
    Django admin mixin for 2FA
    """

    def get_2fa_status(self, obj):
        """Display 2FA status in admin"""
        if TwoFactorAuthService.is_2fa_enabled(obj):
            return '✅ Enabled'
        return '❌ Disabled'
    get_2fa_status.short_description = '2FA Status'

    def enable_2fa_action(self, request, queryset):
        """Admin action to require 2FA for selected users"""
        for user in queryset:
            if not TwoFactorAuthService.is_2fa_enabled(user):
                # Send email/notification to user to set up 2FA
                self.message_user(
                    request,
                    f'2FA setup required for {user.email}'
                )
    enable_2fa_action.short_description = 'Require 2FA for selected users'


# Middleware for 2FA enforcement

class Require2FAMiddleware:
    """
    Middleware to enforce 2FA for staff/admin users
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is staff and accessing admin
        if (
            request.user.is_authenticated and
            request.user.is_staff and
            request.path.startswith('/admin/') and
            not TwoFactorAuthService.is_2fa_enabled(request.user)
        ):
            # Redirect to 2FA setup page
            from django.shortcuts import redirect
            if not request.path.startswith('/admin/setup-2fa/'):
                return redirect('/admin/setup-2fa/')

        response = self.get_response(request)
        return response
