import logging

import dramatiq

from notifications.senders.sendgrid import SendGridSender
from notifications.utils import get_extra_context

logger = logging.getLogger(__name__)


@dramatiq.actor
def worker_health():
    logger.info("OK")


@dramatiq.actor
def send_email(event: str, recipient_list: list, extra_context: dict = None):

    if not extra_context:
        extra_context = {}
    extra_context = get_extra_context(**extra_context)

    sender = SendGridSender()

    sender.send(
        recipient_list=recipient_list,
        event=event,
        context={
            **extra_context,  # type: ignore
        },
    )

    logger.info(f"Sent email to {recipient_list}")


@dramatiq.actor
def raw_send_email(to: list, html_content: str, subject: str, from_email: str):
    sender = SendGridSender()
    sender.raw_send(
        recipient_list=to,
        html_content=html_content,
        subject=subject,
        from_email=from_email,
    )

    logger.info(f"Raw emails sent to {to}")
