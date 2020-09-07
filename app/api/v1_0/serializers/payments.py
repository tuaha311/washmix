from rest_framework import serializers


class CreateIntentSerializer(serializers.Serializer):
    # based on this flag we will handle payment
    is_save_card = serializers.BooleanField(default=True)
    amount = serializers.IntegerField(required=False)


class StripeWebhookSerializer(serializers.Serializer):
    pass
