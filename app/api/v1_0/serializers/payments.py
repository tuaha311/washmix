from rest_framework import serializers

from billing.models import Card


class SetupIntentSerializer(serializers.Serializer):
    pass


class ChargePaymentSerializer(serializers.Serializer):
    # TODO read queryset from request.user.client
    card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)


class StripeWebhookSerializer(serializers.Serializer):
    pass
