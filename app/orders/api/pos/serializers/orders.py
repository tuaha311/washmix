from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from api.fields import BasketField, RequestField
from deliveries.api.serializers.requests import RequestSerializer
from orders.api.pos.serializers.basket import BasketSerializer
from orders.models import Order


class OrderSerializer(CommonContainerSerializer, serializers.ModelSerializer):
    basket = BasketSerializer(allow_null=True)
    request = RequestSerializer(allow_null=True)
    credit_back = serializers.ReadOnlyField()
    dollar_credit_back = serializers.ReadOnlyField()
    subscription = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "basket",
            "request",
            "subscription",
            "invoice_list",
            "status",
            "pretty_status",
            "note",
            "is_save_card",
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
    basket = BasketField(allow_null=True)
    request = RequestField(allow_null=True)

    def validate(self, attrs):
        request = attrs["request"]
        basket = attrs["basket"]

        if Order.objects.filter(basket=basket, request=request).exists():
            raise serializers.ValidationError(
                detail="Order already accepted", code="order_already_accepted",
            )

        return attrs
