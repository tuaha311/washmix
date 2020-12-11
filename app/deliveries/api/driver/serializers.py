from rest_framework import serializers

from deliveries.models import Delivery
from locations.api.serializers.addresses import AddressSerializer
from users.models import Client


class ClientSerializer(serializers.ModelSerializer):
    main_phone = serializers.SlugRelatedField(slug_field="number", read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "main_phone",
            "first_name",
            "last_name",
        ]


class DeliverySerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    client = ClientSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = [
            "id",
            "note",
            "kind",
            "status",
            "date",
            "start",
            "end",
            "address",
            "comment",
            "is_rush",
            "priority",
            "client",
        ]
