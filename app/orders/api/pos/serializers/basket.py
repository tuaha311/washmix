from django.conf import settings

from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from api.fields import POSOrderField
from orders.models import Basket, Order, Price, Quantity
from orders.services.basket import BasketService


class POSBasketClearSerializer(serializers.Serializer):
    order = POSOrderField()


class POSExtraItemSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)
    instructions = serializers.CharField(required=False, allow_null=True)
    dollar_amount = serializers.FloatField(required=False, allow_null=True, read_only=True)


class POSBasketSetExtraItemsSerializer(serializers.Serializer):
    extra_items = POSExtraItemSerializer(many=True)
    order = POSOrderField()

    def validate_order(self, value: Order):
        order = value
        basket = order.basket

        if not basket:
            raise serializers.ValidationError(
                detail="Provide order with basket.",
                code="provide_order_with_basket",
            )

        return value


class POSBasketChangeItemSerializer(serializers.Serializer):
    price = serializers.PrimaryKeyRelatedField(queryset=Price.objects.all())
    count = serializers.IntegerField()
    action = serializers.ChoiceField(choices=settings.BASKET_ACTION_CHOICES)
    order = POSOrderField()

    def validate(self, attrs):
        client = self.context["request"].user.client
        price = attrs["price"]
        count = attrs["count"]
        action = attrs["action"]
        order = attrs["order"]
        basket = order.basket

        service = BasketService(client)
        service.validate(basket, price, count, action)

        return attrs


class POSQuantitySerializer(CommonContainerSerializer, serializers.ModelSerializer):
    id = serializers.IntegerField(source="price.id")
    service = serializers.CharField(source="price.service.title")
    item = serializers.CharField(source="price.item.title")

    class Meta:
        model = Quantity
        fields = [
            "id",
            "count",
            "service",
            "item",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "amount_with_discount",
            "dollar_amount_with_discount",
        ]


class POSBasketSerializer(CommonContainerSerializer, serializers.ModelSerializer):
    item_list = POSQuantitySerializer(many=True, source="quantity_container_list")
    extra_items = POSExtraItemSerializer(many=True)

    class Meta:
        model = Basket
        fields = [
            "id",
            "item_list",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "amount_with_discount",
            "dollar_amount_with_discount",
            "extra_items",
        ]
