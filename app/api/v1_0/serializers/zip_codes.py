from rest_framework import serializers

from core.models import ZipCode


class ZipCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZipCode
        fields = [
            "value",
        ]
