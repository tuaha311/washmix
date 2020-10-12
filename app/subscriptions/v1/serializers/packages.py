from rest_framework import serializers

from subscriptions.models import Package


class PackageSerializer(serializers.ModelSerializer):
    dollar_price = serializers.FloatField()

    class Meta:
        model = Package
        exclude = [
            "created",
            "changed",
        ]
