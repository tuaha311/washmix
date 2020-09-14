from django.contrib.auth import get_user_model

import phonenumbers
from rest_framework import serializers

from core.models import Phone

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
        number = value.strip()

        if not number.startswith("+"):
            raise serializers.ValidationError(
                detail="Invalid phone format.", code="provide_plus",
            )

        if Phone.objects.filter(number__icontains=number).exists():
            raise serializers.ValidationError(
                detail="Invalid credentials.", code="invalid_auth_credentials",
            )

        try:
            Phone.format_number(value)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError(
                detail="Invalid phone format.", code="invalid_phone",
            )

        return value


class EmptyResponseSerializer(serializers.Serializer):
    pass


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
