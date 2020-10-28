from django.conf import settings

from rest_framework import serializers

from api.fields import InvoiceField


class CreateIntentSerializer(serializers.Serializer):
    is_save_card = serializers.BooleanField()
    # this serializer used in many cases where user can have payment method or not
    # 1. welcome scenario (no payment method)
    # 2. subscription purchase (should have method)
    # 3. order processing (should have)
    invoice = InvoiceField()

    def validate(self, attrs):
        invoice = attrs["invoice"]
        is_save_card = attrs["is_save_card"]

        if invoice.subscription.name == settings.PAYC and not is_save_card:
            raise serializers.ValidationError(
                detail="For PAYC package you should save payment card.",
                code="card_save_required_for_payc",
            )

        return attrs


class CreateIntentResponseSerializer(serializers.Serializer):
    public_key = serializers.CharField()
    secret = serializers.CharField()
