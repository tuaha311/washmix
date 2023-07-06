from rest_framework import serializers

from deliveries.models import Delivery
from locations.api.serializers.addresses import AddressSerializer
from users.models import Client


class ClientSerializer(serializers.ModelSerializer):
    main_phone = serializers.SlugRelatedField(slug_field="number", read_only=True)
    client_numbers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Client
        fields = ["id", "main_phone", "first_name", "last_name", "client_numbers", "private_note", "billing_address"]

    def get_client_numbers(self, obj):
        phones = ""
        for ph in obj.phone_list.all():
            if obj.main_phone != ph:
                phones += ph.number + ", "
        return phones


class DeliverySerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)
    changed = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Delivery
        fields = [
            "id",
            "note",
            "order",
            "kind",
            "status",
            "date",
            "start",
            "end",
            "address",
            "comment",
            "is_rush",
            "sorting",
            "client",
            "changed",
        ]
