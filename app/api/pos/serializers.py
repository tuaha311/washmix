from rest_framework import serializers

from billing.models import Coupon
from orders.models import Item, Price, Service


class POSPriceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="item.title", read_only=True)
    image = serializers.ImageField(source="item.image", read_only=True)

    class Meta:
        model = Price
        fields = [
            "id",
            "amount",
            "dollar_amount",
            "title",
            "count",
            "unit",
            "pretty_unit",
            "image",
        ]


class POSServiceSerializer(serializers.ModelSerializer):
    # we show at landing page only certain items
    # some items accessible via pos panel
    item_list = POSPriceSerializer(
        many=True,
        read_only=True,
        source="price_list",
    )

    class Meta:
        model = Service
        exclude = [
            "changed",
            "created",
        ]


class POSItemPriceSerializer(serializers.ModelSerializer):
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


class POSItemSerializer(serializers.ModelSerializer):
    price_list = POSItemPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "title",
            "image",
            "price_list",
        ]


class POSCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
        ]
