from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from pickups.models import Delivery


class DeliverySerializer(serializers.ModelSerializer):
    pickup_date = serializers.DateField()
    dropoff_date = serializers.DateField(required=False)

    class Meta:
        model = Delivery
        exclude = [
            "changed",
            "created",
            "client",
        ]
        extra_kwargs = {
            "dropoff_start": {"required": False},
            "dropoff_end": {"required": False},
        }

    def validate_address(self, value):
        client = self.context["request"].user.client
        get_object_or_404(client.address_list.all(), pk=value.pk)
        return value

    def validate(self, attrs):
        if attrs["pickup_start"] >= attrs["pickup_end"]:
            raise serializers.ValidationError(
                detail="Start time can't be earlier than end", code="start_earlier_than_end",
            )

        return attrs
