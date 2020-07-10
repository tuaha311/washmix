from rest_framework import serializers

from core.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = [
            "user",
        ]
