from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from pickups.models import Delivery, Interval


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        exclude = [
            "changed",
            "created",
            "client",
        ]

    def validate_address(self, value):
        client = self.context["request"].user.client
        get_object_or_404(client.address_list.all(), pk=value.pk)
        return value
