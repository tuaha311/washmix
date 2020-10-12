from rest_framework import serializers

from locations.models import ZipCode


class ZipCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZipCode
        exclude = [
            "created",
            "changed",
        ]
