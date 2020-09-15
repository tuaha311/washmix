from django.conf import settings

from rest_framework import serializers


class FlexWebhookSerializer(serializers.Serializer):
    """
    Request data from Twilio Flex Widget:
    {
        "message": "{{trigger.message.Body}}",
        "contact": "{{trigger.message.From}}",
        "datetime": "{{trigger.message.DateCreated}}",
        "channel": "{{trigger.message.ChannelAttributes.channel_type}}"
    }
    """

    message = serializers.CharField()
    contact = serializers.CharField()
    datetime = serializers.DateTimeField(input_formats=[settings.TWILIO_DATETIME_FORMAT])
    channel = serializers.CharField()
