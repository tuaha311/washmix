from __future__ import absolute_import

import dramatiq
# from celery import shared_task
from twilio.rest import Client

from core.models import Order
from middleware import TwilioNotificationsMiddleware

# Uses credentials from the TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
# environment variables
client = Client()


@dramatiq.actor
def send_sms_reminder(order_id, message, phone):
    """Send a reminder to a phone using Twilio SMS"""
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        # The order we were trying to remind someone about
        # has been deleted, so we don't need to do anything
        return

    notification = TwilioNotificationsMiddleware(order.user)
    notification.process_message(message, "+" + phone)
