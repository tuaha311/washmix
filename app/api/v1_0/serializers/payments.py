from rest_framework import serializers


class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=9, decimal_places=2)
    currency = serializers.CharField()


class ChargePaymentSerializer(serializers.Serializer):
    pass


class StripeWebhookSerializer(serializers.Serializer):
    pass
