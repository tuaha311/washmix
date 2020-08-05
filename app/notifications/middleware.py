from __future__ import unicode_literals

import os

from django.core.exceptions import MiddlewareNotUsed

from twilio.rest import Client

from notifications.models import Notification


def load_twilio_config():
    twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_NUMBER")

    if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
        raise MiddlewareNotUsed

    return (twilio_number, twilio_account_sid, twilio_auth_token)


class MessageClient(object):
    def __init__(self):
        (twilio_number, twilio_account_sid, twilio_auth_token) = load_twilio_config()

        self.twilio_number = twilio_number
        self.twilio_client = Client(twilio_account_sid, twilio_auth_token)

    def send_message(self, body, to):
        self.twilio_client.messages.create(
            body=body, to=to, from_=self.twilio_number,
        )


class TwilioNotificationsMiddleware(object):
    def __init__(self, user):
        self.client = MessageClient()
        self.user = user

    def process_message(self, message_to_send, to):
        try:
            self.client.send_message(message_to_send, to)
        except Exception:
            return
        Notification.objects.create(user=self.user, message=message_to_send)
