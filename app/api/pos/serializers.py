from rest_framework import serializers

from billing.models import Coupon
from orders.models import Item, Price


class ItemPriceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="service.title", read_only=True)
    image = serializers.ImageField(source="service.image", read_only=True)

    class Meta:
        model = Price
        fields = [
            "id",
            "count",
            "unit",
            "pretty_unit",
            "amount",
            "dollar_amount",
            "title",
            "image",
        ]


class ItemSerializer(serializers.ModelSerializer):
    price_list = ItemPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "title",
            "image",
            "price_list",
        ]


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
        ]
