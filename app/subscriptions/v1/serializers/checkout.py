from rest_framework import serializers

from api.fields import InvoiceField
from billing.validators import validate_client_can_pay


class SubscriptionCheckoutSerializer(serializers.Serializer):
    # at this moment client should have payment method
    # 1. upgrade subscription plan (should have payment method)
    invoice = InvoiceField(validators=[validate_client_can_pay])
