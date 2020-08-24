from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from billing.models import Card


class CardSerializer(serializers.ModelSerializer):
    stripe_id = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        label="Stripe ID",
        max_length=100,
        validators=[UniqueValidator(queryset=Card.objects.all())],
    )

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
