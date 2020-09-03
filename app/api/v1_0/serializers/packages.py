from rest_framework import serializers

from billing.models import Package


class PackageSerializer(serializers.ModelSerializer):
    dollar_price = serializers.FloatField()

    class Meta:
        model = Package
        exclude = [
            "created",
            "changed",
        ]
