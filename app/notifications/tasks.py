import logging

import dramatiq

from notifications.context import email_context
from notifications.senders.sendgrid import SendGridSender
from notifications.utils import get_extra_context
from users.models import Client

logger = logging.getLogger(__name__)


@dramatiq.actor
def worker_health():
    logger.info("OK")


@dramatiq.actor
def send_email(event: str, client_id: int, extra_context: dict = None):
    client = Client.objects.get(id=client_id)
    email = client.email

    if not extra_context:
        extra_context = {}
    extra_context = get_extra_context(**extra_context)

    sender = SendGridSender()

    sender.send(
        recipient_list=[client.email],
        event=event,
        context={
            "client": client,
            "washmix": email_context,
            **extra_context,
        },
    )

    logger.info(f"Sent to email {email}")


@dramatiq.actor
def raw_send_email(to: list, html_content: str, subject: str, from_email: str):
    sender = SendGridSender()
    sender.raw_send(
        recipient_list=to,
        html_content=html_content,
        subject=subject,
        from_email=from_email,
    )

    logger.info(f"Raw sent to emails {to}")
