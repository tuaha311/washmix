from rest_framework import serializers

from locations.models import Address, ZipCode


class CheckoutUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=100)


class CheckoutAddressSerializer(serializers.ModelSerializer):
    zip_code = serializers.SlugRelatedField(slug_field="value", queryset=ZipCode.objects.all())
    title = serializers.CharField(default="Main", required=False)

    class Meta:
        model = Address
        exclude = [
            "client",
        ]


class CheckoutSerializer(serializers.Serializer):
    user = CheckoutUserSerializer()
    address = CheckoutAddressSerializer()
