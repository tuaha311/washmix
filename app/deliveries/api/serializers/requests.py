from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from deliveries.models import Request
from deliveries.services.requests import RequestService
from locations.models import Address


class RequestSerializer(serializers.ModelSerializer):
    pickup_date = serializers.DateField()

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
        ]
        extra_kwargs = {
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

        if "pickup_date" in attrs:
            pickup_date = attrs["pickup_date"]

            service = RequestService(client=client, pickup_date=pickup_date)
            service.validate()

        return attrs
