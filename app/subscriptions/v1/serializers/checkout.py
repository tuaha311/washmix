from rest_framework import serializers

from api.fields import InvoiceField
from billing.validators import validate_invoice


class SubscriptionCheckoutSerializer(serializers.Serializer):
    invoice = InvoiceField(validators=[validate_invoice])
