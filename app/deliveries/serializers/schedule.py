from rest_framework import serializers

from deliveries.models import Schedule


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        exclude = [
            "client",
        ]
