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
        is_rush = attrs.get("is_rush", False)

        if "pickup_date" in attrs:
            pickup_date = attrs["pickup_date"]

            service = RequestService(client=client, pickup_date=pickup_date, is_rush=is_rush)
            service.validate()

        return attrs


class RequestCheckSerializer(serializers.Serializer):
    pickup_date = serializers.DateField()
    pickup_start = serializers.TimeField()

    def validate(self, attrs):
        client = self.context["request"].user.client
        pickup_date = attrs["pickup_date"]
        pickup_start = attrs["pickup_start"]

        service = RequestService(client=client, pickup_date=pickup_date, pickup_start=pickup_start)
        service.validate()

        return attrs
    
class ChargeCustomerSerializer(serializers.Serializer):
    client_id = serializers.IntegerField()
    order_items = serializers.ListField(child=serializers.IntegerField(), required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    waive_delivery_charge = serializers.BooleanField(required=False)
    rush_service_charge = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)