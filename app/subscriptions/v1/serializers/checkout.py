from rest_framework import serializers

from api.fields import InvoiceField
from billing.validators import validate_paid_invoice, validate_payment_method


class SubscriptionCheckoutSerializer(serializers.Serializer):
    invoice = InvoiceField(validators=[validate_paid_invoice])

    def validate(self, attrs):
        client = self.context["request"].user.client

        validate_payment_method(client)

        return attrs
