from django.conf import settings

from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from orders.models import Basket, Price, Quantity
from orders.services.basket import BasketService


class ExtraItemSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, allow_null=True)
    instructions = serializers.CharField(required=False, allow_null=True)
    amount = serializers.IntegerField(required=True, allow_null=True)
    dollar_amount = serializers.FloatField(required=False, allow_null=True)


class BasketSetExtraItemsSerializer(serializers.Serializer):
    extra_items = ExtraItemSerializer(many=True)


class BasketChangeItemSerializer(serializers.Serializer):
    price = serializers.PrimaryKeyRelatedField(queryset=Price.objects.all())
    count = serializers.IntegerField()
    action = serializers.ChoiceField(choices=settings.BASKET_ACTION_CHOICES)

    def validate(self, attrs):
        client = self.context["request"].user.client
        price = attrs["price"]
        count = attrs["count"]
        action = attrs["action"]

        service = BasketService(client)
        service.validate(price, count, action)

        return attrs


class QuantitySerializer(CommonContainerSerializer, serializers.ModelSerializer):
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


class BasketSerializer(CommonContainerSerializer, serializers.ModelSerializer):
    item_list = QuantitySerializer(many=True, source="quantity_container_list")
    extra_items = ExtraItemSerializer(many=True)

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
