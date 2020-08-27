from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from billing.models import Card
from locations.models import Address, ZipCode
from users.models import Client


class CheckoutUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=100)

    class Meta:
        model = Client
        fields = [
            "first_name",
            "last_name",
        ]


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
    card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())

    def validate_card(self, value):
        client = self.context["request"].user.client

        get_object_or_404(client.card_list.all(), pk=value.pk)

        return value
