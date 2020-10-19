from django.conf import settings

from rest_framework import serializers

from api.v1_0.serializers.common import CommonAmountWithDiscountSerializer
from orders.models import Basket, Price, Quantity
from orders.services.basket import BasketService


class ChangeItemSerializer(serializers.Serializer):
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


class QuantitySerializer(CommonAmountWithDiscountSerializer, serializers.ModelSerializer):
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


class BasketSerializer(CommonAmountWithDiscountSerializer, serializers.ModelSerializer):
    item_list = QuantitySerializer(many=True, source="quantity_list")

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
        ]
