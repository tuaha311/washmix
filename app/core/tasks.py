import logging

import dramatiq

from notifications.context import email_context
from notifications.senders.sendgrid import SendGridSender


@dramatiq.actor
def count(n: int):
    for item in range(n):
        logging.info(item)


@dramatiq.actor
def send_email(email: str, event: str, full_name: str = ""):
    sender = SendGridSender()
    sender.send(
        recipient_list=[email],
        event=event,
        context={"email": email, "full_name": email, "washmix": email_context,},
    )

    logging.info(f"Sent to email {email}")


@dramatiq.actor
def raw_send_email(to: list, html_content: str, subject: str, from_email: str):
    sender = SendGridSender()
    sender.raw_send(
        recipient_list=to, html_content=html_content, subject=subject, from_email=from_email,
    )

    logging.info(f"Raw sent to emails [to]")
