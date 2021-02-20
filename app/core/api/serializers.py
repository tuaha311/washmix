from rest_framework import serializers

from core.models import Phone
from core.utils import get_clean_number


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        exclude = [
            "client",
            "created",
            "changed",
        ]

    def validate_phone(self, value):
        number = get_clean_number(value)

        if Phone.objects.filter(number=number).exists():
            raise serializers.ValidationError(
                detail="Invalid credentials.",
                code="invalid_auth_credentials",
            )

        return value
