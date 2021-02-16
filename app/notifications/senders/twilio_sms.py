import logging

from django.conf import settings
from django.template.loader import render_to_string

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioClient

from notifications.senders.base import Sender

logger = logging.getLogger(__name__)


class TwilioSender(Sender):
    def __init__(self):
        self._twilio_client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def send(self, recipient_list: list, event: str, context: dict = None, *args, **kwargs):
        event_info = settings.SMS_EVENT_INFO[event]

        template_name = event_info["template_name"]
        from_number = event_info.get("from_number", settings.TWILIO_NUMBER)

        body = render_to_string(template_name, context=context)

        self.raw_send(
            from_sender=from_number,
            recipient_list=recipient_list,
            body=body,
            subject="",
        )

    def raw_send(
        self,
        from_sender: str,
        recipient_list: list,
        subject: str,
        body: str,
        *args,
        **kwargs,
    ):
        twilio_client = self._twilio_client

        for recipient in recipient_list:
            try:
                response = twilio_client.messages.create(
                    to=recipient,
                    body=body,
                    from_=from_sender,
                )
            except TwilioRestException:
                continue

            logger.info(f"Twilio response - {response}")
