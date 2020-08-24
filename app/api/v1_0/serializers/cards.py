from rest_framework import serializers

from billing.models import Card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        exclude = [
            "created",
            "changed",
            "client",
        ]
        read_only_fields = [
            "is_active",
        ]
