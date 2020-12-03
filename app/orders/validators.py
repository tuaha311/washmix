from rest_framework import serializers

from orders.models import Order


def check_order(value: Order):
    order = value
    basket = order.basket

    if not basket:
        raise serializers.ValidationError(
            detail="Provide order with basket.",
            code="provide_order_with_basket",
        )

    return value
