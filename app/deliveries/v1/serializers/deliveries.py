from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from deliveries.models import Delivery
from deliveries.services.delivery import DeliveryService
from locations.models import Address


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
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
        extra_kwargs = {
            "pickup_date": {"required": True},
            "pickup_start": {"required": False, "read_only": True},
            "pickup_end": {"required": False, "read_only": True},
            "dropoff_date": {"required": False, "read_only": True},
            "dropoff_start": {"required": False, "read_only": True},
            "dropoff_end": {"required": False, "read_only": True},
            "address": {"allow_null": False, "required": True},
            "schedule": {"read_only": True},
        }

    def validate_address(self, value: Address):
        client = self.context["request"].user.client
        get_object_or_404(client.address_list.all(), pk=value.pk)
        return value

    def validate(self, attrs: dict):
        client = self.context["request"].user.client
        pickup_date = attrs["pickup_date"]

        service = DeliveryService(client=client, pickup_date=pickup_date)
        service.validate()

        return attrs
