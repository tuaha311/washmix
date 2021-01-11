import logging

import dramatiq

from notifications.senders.sendgrid import SendGridSender
from notifications.senders.twilio_sms import TwilioSender
from notifications.utils import get_extra_context

logger = logging.getLogger(__name__)


@dramatiq.actor
def worker_health():
    logger.info("OK")


def _common_send_handler(
    sender_class, event: str, recipient_list: list, extra_context: dict = None
):
    if not extra_context:
        extra_context = {}
    extra_context = get_extra_context(**extra_context)

    sender = sender_class()

    sender.send(
        recipient_list=recipient_list,
        event=event,
        context={
            **extra_context,  # type: ignore
        },
    )


@dramatiq.actor
def send_email(event: str, recipient_list: list, extra_context: dict = None):
    _common_send_handler(
        sender_class=SendGridSender,
        event=event,
        recipient_list=recipient_list,
        extra_context=extra_context,
    )

    logger.info(f"Sent email via SendGrid to {recipient_list}")


@dramatiq.actor
def raw_send_email(to: list, html_content: str, subject: str, from_email: str):
    sender = SendGridSender()
    sender.raw_send(
        recipient_list=to,
        body=html_content,
        subject=subject,
        from_sender=from_email,
    )

    logger.info(f"Raw emails sent via SendGrid to {to}")


@dramatiq.actor
def send_sms(event: str, recipient_list: list, extra_context: dict = None):
    _common_send_handler(
        sender_class=TwilioSender,
        event=event,
        recipient_list=recipient_list,
        extra_context=extra_context,
    )

    logger.info("Sent SMS via Twilio to {recipient_list}")
