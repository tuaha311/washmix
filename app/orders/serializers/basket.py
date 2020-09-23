from django.conf import settings

from rest_framework import serializers

from orders.models import Price, Quantity
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


class ChangeItemResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quantity
        fields = "__all__"
