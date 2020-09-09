from rest_framework import serializers

from api.fields import InvoiceField


class CreateIntentSerializer(serializers.Serializer):
    is_save_card = serializers.BooleanField()
    invoice = InvoiceField()


class CreateIntentResponseSerializer(serializers.Serializer):
    public_key = serializers.CharField()
    secret = serializers.CharField()
