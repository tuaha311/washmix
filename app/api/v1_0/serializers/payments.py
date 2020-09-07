from rest_framework import serializers

from api.fields import InvoiceField


class CreateIntentSerializer(serializers.Serializer):
    is_save_card = serializers.BooleanField()
    invoice = InvoiceField()


class StripeWebhookSerializer(serializers.Serializer):
    pass
