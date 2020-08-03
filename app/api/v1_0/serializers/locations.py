from rest_framework import serializers

from locations.models import City


class LocationSerializer(serializers.ModelSerializer):
    zipcode_list = serializers.SlugRelatedField(many=True, read_only=True, slug_field="value",)

    class Meta:
        model = City
        exclude = [
            "changed",
            "created",
        ]
