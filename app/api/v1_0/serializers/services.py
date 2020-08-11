from rest_framework import serializers

from orders.models import Price, Service


class PriceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="item.title", read_only=True)
    image = serializers.ImageField(source="item.image", read_only=True)

    class Meta:
        model = Price
        fields = [
            "id",
            "value",
            "title",
            "count",
            "unit",
            "image",
        ]


class ServiceSerializer(serializers.ModelSerializer):
    item_list = PriceSerializer(many=True, read_only=True, source="price_list",)

    class Meta:
        model = Service
        exclude = [
            "changed",
            "created",
        ]
