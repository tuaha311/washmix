from rest_framework import serializers

from core.models import Package


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        exclude = [
            "created",
            "changed",
        ]
