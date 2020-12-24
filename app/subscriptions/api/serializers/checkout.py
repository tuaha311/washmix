from rest_framework import serializers

from api.fields import OrderField
from billing.validators import validate_client_can_pay, validate_saved_cards
from orders.choices import PaymentChoices


class SubscriptionCheckoutSerializer(serializers.Serializer):
    # at this moment client should have payment method
    # 1. upgrade subscription plan (should have payment method)
    order = OrderField(validators=[validate_client_can_pay, validate_saved_cards])

    def validate_order(self, value):
        """
        Here we are preventing duplicate checkout on paid orders.
        """

        order = value

        if order.payment == PaymentChoices.PAID:
            raise serializers.ValidationError(
                detail="Order already paid.",
                code="order_paid",
            )

        return value
