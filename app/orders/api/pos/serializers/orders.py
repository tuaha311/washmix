from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from api.fields import OrderField
from deliveries.api.client.serializers.requests import RequestSerializer
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
    order = OrderField()
