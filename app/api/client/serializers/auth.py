from django.contrib.auth import get_user_model

from djoser.conf import settings as djoser_settings
from djoser.serializers import PasswordResetConfirmSerializer, SendEmailResetSerializer
from rest_framework import serializers

from api.utils import cleanup_email
from core.models import Phone
from core.utils import get_clean_number

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    phone = serializers.CharField()

    def validate_email(self, value):
        email = cleanup_email(value)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                detail="Invalid credentials.",
                code="invalid_auth_credentials",
            )

        return value

    def validate_phone(self, value):
        number = get_clean_number(value)

        if Phone.objects.filter(number=number).exists():
            raise serializers.ValidationError(
                detail="Invalid credentials.",
                code="invalid_auth_credentials",
            )

        return value


class EmptyResponseSerializer(serializers.Serializer):
    pass


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()


class DjoserUserFunctionsMixin:
    def get_user(self, is_active=True):
        """
        Custom implementation of `djoser.serializers.UserFunctionsMixin` with
        clean email.
        """

        try:
            email = self.data.get(self.email_field, "")
            clean_email = cleanup_email(email)
            user = User._default_manager.get(
                is_active=is_active,
                **{self.email_field: clean_email},
            )
            if user.has_usable_password():
                return user
        except User.DoesNotExist:
            pass
        if (
            djoser_settings.PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND
            or djoser_settings.USERNAME_RESET_SHOW_EMAIL_NOT_FOUND
        ):
            self.fail("email_not_found")


class DjoserSendEmailResetSerializer(
    DjoserUserFunctionsMixin,
    SendEmailResetSerializer,
):
    pass


class DjoserPasswordResetConfirmSerializer(
    DjoserUserFunctionsMixin,
    PasswordResetConfirmSerializer,
):
    pass
