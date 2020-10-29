from django.conf import settings

from rest_framework import serializers

from api.fields import OrderField
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


class WelcomeCheckoutBillingAddressSerializer(serializers.Serializer):
    zip_code = serializers.CharField(max_length=10)
    address_line_1 = serializers.CharField(max_length=250)
    address_line_2 = serializers.CharField(max_length=250, allow_blank=True, required=False)


class WelcomeCheckoutAddressSerializer(serializers.ModelSerializer):
    zip_code = serializers.SlugRelatedField(slug_field="value", queryset=ZipCode.objects.all())
    title = serializers.CharField(default=settings.MAIN_TITLE, required=False)

    class Meta:
        model = Address
        exclude = [
            "client",
        ]


class WelcomeCheckoutSerializer(serializers.Serializer):
    user = WelcomeCheckoutUserSerializer()
    address = WelcomeCheckoutAddressSerializer()
    billing_address = WelcomeCheckoutBillingAddressSerializer()
    # at this moment client doesn't have an payment methods
    # 1. welcome scenario (no payment method)
    order = OrderField()


class WelcomeCheckoutResponseSerializer(serializers.Serializer):
    user = WelcomeCheckoutUserSerializer()
    address = WelcomeCheckoutAddressSerializer()
    billing_address = WelcomeCheckoutBillingAddressSerializer()
