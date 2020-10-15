from rest_framework import serializers

from api.fields import InvoiceField
from billing.validators import validate_paid_invoice, validate_payment_method
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
    invoice = InvoiceField(validators=[validate_paid_invoice])

    def validate(self, attrs):
        client = self.context["request"].user.client

        validate_payment_method(client)

        return attrs


class WelcomeCheckoutResponseSerializer(serializers.Serializer):
    user = WelcomeCheckoutUserSerializer()
    address = WelcomeCheckoutAddressSerializer()
    billing_address = WelcomeCheckoutAddressSerializer()
