from django.conf import settings

from rest_framework import serializers

from api.fields import OrderField


class CreateIntentSerializer(serializers.Serializer):
    is_save_card = serializers.BooleanField()
    order = OrderField(default=None, required=False)

    def validate(self, attrs):
        order = attrs["order"]
        is_save_card = attrs["is_save_card"]

        if not order and not is_save_card:
            raise serializers.ValidationError(
                detail="To bind a new payment method you should save a card.",
                code="card_save_required_to_bind",
            )

        if order and order.subscription.name == settings.PAYC and not is_save_card:
            raise serializers.ValidationError(
                detail="For PAYC package you should save payment card.",
                code="card_save_required_for_payc",
            )

        return attrs


class CreateIntentResponseSerializer(serializers.Serializer):
    public_key = serializers.CharField()
    secret = serializers.CharField()
