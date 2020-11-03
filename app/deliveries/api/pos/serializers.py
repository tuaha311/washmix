from rest_framework import serializers

from api.client.serializers.common import CommonContainerSerializer
from api.fields import RequestField
from deliveries.models import Request


class RequestChooseSerializer(serializers.Serializer):
    request = RequestField()


class RequestResponseSerializer(CommonContainerSerializer, serializers.ModelSerializer):
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
            "comment",
            "schedule",
            "amount",
            "dollar_amount",
            "discount",
            "dollar_discount",
            "amount_with_discount",
            "dollar_amount_with_discount",
        ]
