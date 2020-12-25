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
        subscription = order.subscription
        client = self.context["request"].user.client

        if not subscription:
            raise serializers.ValidationError(
                detail="Provide order for subscription.",
                code="provide_order_for_subscription",
            )

        if order.payment == PaymentChoices.PAID:
            raise serializers.ValidationError(
                detail="Order already paid.",
                code="order_paid",
            )

        if client.subscription and client.subscription.name == subscription.name:
            raise serializers.ValidationError(
                detail="You already have this subscription.",
                code="already_at_this_subscription",
            )

        return value
