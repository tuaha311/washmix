from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from orders.models import Order
from subscriptions.models import Package


class SubscriptionChooseSerializer(serializers.Serializer):
    package = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Package.objects.all(),
    )


class SubscriptionChooseResponseSerializer(CommonContainerSerializer, serializers.ModelSerializer):
    subscription = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Order
        fields = [
            "id",
            "subscription",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "amount_with_discount",
            "dollar_amount_with_discount",
        ]
