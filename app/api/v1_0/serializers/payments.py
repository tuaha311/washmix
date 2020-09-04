from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from billing.models import Card


class SetupIntentSerializer(serializers.Serializer):
    card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())

    def validate_card(self, value):
        client = self.context["request"].user.client

        get_object_or_404(client.card_list.all(), pk=value.pk)

        return value


class StripeWebhookSerializer(serializers.Serializer):
    pass
