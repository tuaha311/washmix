from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import Phone
from core.utils import get_clean_number

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    phone = serializers.CharField()

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                detail="Invalid credentials.", code="invalid_auth_credentials",
            )

        return value

    def validate_phone(self, value):
        number = get_clean_number(value)

        if Phone.objects.filter(number=number).exists():
            raise serializers.ValidationError(
                detail="Invalid credentials.", code="invalid_auth_credentials",
            )

        return value


class EmptyResponseSerializer(serializers.Serializer):
    pass


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
