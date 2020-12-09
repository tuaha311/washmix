from rest_framework import serializers

from deliveries.models import Delivery
from locations.api.serializers.addresses import AddressSerializer


class DeliverySerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = [
            "id",
            "kind",
            "status",
            "date",
            "start",
            "end",
            "address",
            "comment",
            "is_rush",
        ]
