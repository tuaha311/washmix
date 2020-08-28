import logging

import dramatiq

from notifications.senders.sendgrid import SendGridSender


@dramatiq.actor
def count(n: int):
    for item in range(n):
        logging.info(item)


@dramatiq.actor
def send_email(email: str, event: str):
    sender = SendGridSender()
    sender.send(
        recipient_list=[email], event=event, context={"user": email},
    )

    logging.info(f"Email sent to {email}")
