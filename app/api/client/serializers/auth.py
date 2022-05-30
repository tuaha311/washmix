from django.contrib.auth import get_user_model

from djoser.conf import settings as djoser_settings
from djoser.serializers import PasswordResetConfirmSerializer, SendEmailResetSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSlidingSerializer
from notifications.tasks import send_email
from django.conf import settings
from api.utils import cleanup_email
from core.models import Phone
from core.utils import get_clean_number
from locations.models import ZipCode
from users.models import Log

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    phone = serializers.CharField()
    zipCode = serializers.SlugRelatedField(slug_field="value", queryset=ZipCode.objects.all())
    addressLine1 = serializers.CharField()

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


class LoginSerializer(TokenObtainSlidingSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if "token" in data and data["token"]:
            Log.objects.create(customer=self.user.email, action="Log In")

        return data


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
