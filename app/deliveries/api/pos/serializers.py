from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from deliveries.models import Request


class RequestResponseSerializer(CommonContainerSerializer, serializers.ModelSerializer):
    is_free = serializers.BooleanField(read_only=True)
    dollar_rush_amount = serializers.ReadOnlyField()
    dollar_custom_amount = serializers.ReadOnlyField()

    class Meta:
        model = Request
        fields = [
            "id",
            "address",
            "pickup_date",
            "pickup_start",
            "pickup_end",
            "dropoff_date",
            "dropoff_start",
            "dropoff_end",
            "is_rush",
            "is_free",
            "comment",
            "schedule",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "amount_with_discount",
            "dollar_amount_with_discount",
            "rush_amount",
            "dollar_rush_amount",
            "custom_amount",
            "dollar_custom_amount",
        ]


class POSRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = [
            "order",
            "is_rush",
            "rush_amount",
            "is_custom",
            "custom_amount",
        ]
