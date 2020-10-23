from rest_framework import serializers

from api.fields import BasketField, RequestField
from deliveries.v1.serializers.requests import RequestSerializer
from orders.models import Order
from orders.v1.serializers.basket import BasketSerializer


class OrderSerializer(serializers.ModelSerializer):
    basket = BasketSerializer()
    request = RequestSerializer()

    class Meta:
        model = Order
        exclude = [
            "created",
            "changed",
            "client",
            "employee",
        ]


class OrderCheckoutSerializer(serializers.Serializer):
    request = RequestField()
    basket = BasketField()

    def validate(self, attrs):
        request = attrs["request"]
        basket = attrs["basket"]

        if Order.objects.filter(basket=basket, request=request).exists():
            raise serializers.ValidationError(
                detail="Order already accepted", code="order_already_accepted",
            )

        return attrs
