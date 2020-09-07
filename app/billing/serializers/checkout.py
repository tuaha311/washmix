from rest_framework import serializers

from api.fields import InvoiceField
from billing.stripe_helper import StripeHelper
from locations.models import Address, ZipCode
from users.models import Client


class CheckoutUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=100)

    class Meta:
        model = Client
        fields = [
            "first_name",
            "last_name",
            "is_auto_billing",
        ]


class CheckoutAddressSerializer(serializers.ModelSerializer):
    zip_code = serializers.SlugRelatedField(slug_field="value", queryset=ZipCode.objects.all())
    title = serializers.CharField(default="Main", required=False)

    class Meta:
        model = Address
        exclude = [
            "client",
        ]


class CheckoutSerializer(serializers.Serializer):
    user = CheckoutUserSerializer()
    address = CheckoutAddressSerializer()
    invoice = InvoiceField()
    is_save_card = serializers.BooleanField(default=True)

    def validate(self, attrs):
        client = self.context["request"].user.client
        stripe_helper = StripeHelper(client)

        if not stripe_helper.payment_method_list:
            raise serializers.ValidationError(
                detail="You have no active payment methods.", code="no_payment_methods",
            )

        return attrs
