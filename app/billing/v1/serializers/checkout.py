from rest_framework import serializers

from api.fields import InvoiceField
from locations.models import Address, ZipCode
from users.models import Client


class WelcomeCheckoutUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=100)
    is_auto_billing = serializers.BooleanField()

    class Meta:
        model = Client
        fields = [
            "first_name",
            "last_name",
            "is_auto_billing",
        ]


class WelcomeCheckoutAddressSerializer(serializers.ModelSerializer):
    zip_code = serializers.SlugRelatedField(slug_field="value", queryset=ZipCode.objects.all())
    title = serializers.CharField(default="Main", required=False)

    class Meta:
        model = Address
        exclude = [
            "client",
        ]


class WelcomeCheckoutSerializer(serializers.Serializer):
    user = WelcomeCheckoutUserSerializer()
    address = WelcomeCheckoutAddressSerializer()
    billing_address = WelcomeCheckoutAddressSerializer()
    # at this moment client doesn't have an payment methods
    # 1. welcome scenario (no payment method)
    invoice = InvoiceField()


class WelcomeCheckoutResponseSerializer(serializers.Serializer):
    user = WelcomeCheckoutUserSerializer()
    address = WelcomeCheckoutAddressSerializer()
    billing_address = WelcomeCheckoutAddressSerializer()
