from rest_framework import serializers

from orders.models import Price, Service


class PriceSerializer(serializers.ModelSerializer):
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


class ServiceSerializer(serializers.ModelSerializer):
    # we show at landing page only certain items
    # some items accessible via pos panel
    item_list = PriceSerializer(many=True, read_only=True, source="visible_price_list",)

    class Meta:
        model = Service
        exclude = [
            "changed",
            "created",
        ]
