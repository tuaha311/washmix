from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from api.fields import OrderField, POSClientField, POSRequestField
from deliveries.api.pos.serializers import RequestResponseSerializer
from orders.api.pos.serializers.basket import BasketSerializer
from orders.models import Order


class OrderSerializer(CommonContainerSerializer, serializers.ModelSerializer):
    basket = BasketSerializer(allow_null=True)
    request = RequestResponseSerializer(allow_null=True)
    subscription = serializers.SlugRelatedField(slug_field="name", read_only=True, allow_null=True)
    credit_back = serializers.ReadOnlyField()
    dollar_credit_back = serializers.ReadOnlyField()

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


class OrderPrepareSerializer(serializers.Serializer):
    client = POSClientField()
    request = POSRequestField()

    def validate(self, attrs):
        client = attrs["client"]
        request = attrs["request"]

        if request not in client.request_list.all():
            raise serializers.ValidationError(
                detail="Client doesn't have this request pickup.",
                code="request_pickup_not_found",
            )

        return attrs
