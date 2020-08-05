import dramatiq

from notifications.middleware import TwilioNotificationsMiddleware
from orders.models import Order


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
