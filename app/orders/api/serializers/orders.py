from rest_framework import serializers

from api.client.serializers.common import CommonAmountWithDiscountSerializer
from api.fields import BasketField, RequestField
from deliveries.api.serializers.requests import RequestSerializer
from orders.api.serializers.basket import BasketSerializer
from orders.models import Order


class OrderSerializer(CommonAmountWithDiscountSerializer, serializers.ModelSerializer):
    basket = BasketSerializer()
    request = RequestSerializer()
    credit_back = serializers.ReadOnlyField()
    dollar_credit_back = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id",
            "basket",
            "request",
            "invoice_list",
            "status",
            "pretty_status",
            "credit_back",
            "dollar_credit_back",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "amount_with_discount",
            "dollar_amount_with_discount",
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
