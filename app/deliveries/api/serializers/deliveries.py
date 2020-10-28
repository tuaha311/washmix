from rest_framework import serializers

from deliveries.models import Delivery


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        exclude = [
            "created",
            "changed",
            "employee",
        ]
