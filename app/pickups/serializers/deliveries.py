from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from locations.models import Address
from pickups.models import Delivery
from pickups.services.delivery import DeliveryService


class DeliverySerializer(serializers.ModelSerializer):
    pickup_date = serializers.DateField()
    dropoff_date = serializers.DateField(required=False, read_only=True)

    class Meta:
        model = Delivery
        exclude = [
            "changed",
            "created",
            "client",
        ]
        extra_kwargs = {
            "dropoff_start": {"required": False, "read_only": True},
            "dropoff_end": {"required": False, "read_only": True},
        }

    def validate_address(self, value: Address):
        client = self.context["request"].user.client
        get_object_or_404(client.address_list.all(), pk=value.pk)
        return value

    def validate(self, attrs: dict):
        client = self.context["request"].user.client
        service = DeliveryService(
            client=client,
            pickup_date=attrs["pickup_date"],
            pickup_start=attrs["pickup_start"],
            pickup_end=attrs["pickup_end"],
        )

        service.validate()

        return attrs
