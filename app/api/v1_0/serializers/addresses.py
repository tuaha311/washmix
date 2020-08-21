from rest_framework import serializers

from locations.models import Address, ZipCode


class AddressSerializer(serializers.ModelSerializer):
    zip_code = serializers.SlugRelatedField(slug_field="value", queryset=ZipCode.objects.all())

    class Meta:
        model = Address
        exclude = [
            "client",
        ]
