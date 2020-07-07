from drf_writable_nested.serializers import WritableNestedModelSerializer
from core.models import Product
from rest_framework import serializers


class ProductItemSerializer(WritableNestedModelSerializer):

    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True)
    price = serializers.FloatField(required=False)

    class Meta:
        model = Product
        fields = ("id", "name", "price")


class ProductSerializer(WritableNestedModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True)
    price = serializers.FloatField(required=False)
    children = ProductItemSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ("id", "name", "price", "children")
