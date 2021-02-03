import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from deliveries.choices import Kind, Status
from deliveries.models import Delivery
from notifications.tasks import send_sms

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Delivery, dispatch_uid="on_delivery_notify_signal")
def on_delivery_notify_signal(
    instance: Delivery, created: bool, raw: bool, update_fields: frozenset, **kwargs
):
    """
    Signal handler that sends SMS when Delivery:
        - Created
        - Date is changed
    """

    # We are ignoring raw signals
    # Ref - https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
    if raw:
        logger.info("Raw signal call - ignoring")
        return None

    delivery = instance
    client = delivery.client
    number = client.main_phone.number
    is_created = created
    is_date_updated = False
    is_dropoff = delivery.kind == Kind.DROPOFF
    is_pickup = delivery.kind == Kind.PICKUP
    is_completed = delivery.status == Status.COMPLETED

    if update_fields:
        is_date_updated = "date" in update_fields

    if is_pickup and (is_created or is_date_updated):
        send_sms.send(
            event=settings.NEW_DELIVERY,
            recipient_list=[number],
            extra_context={
                "client_id": client.id,
                "delivery_id": delivery.id,
            },
        )

        logger.info(f"Sending SMS to client {client.email}")

    if is_dropoff and is_completed:
        send_sms.send(
            event=settings.DELIVERY_DROPOFF_COMPLETE,
            recipient_list=[number],
            extra_context={
                "client_id": client.id,
                "delivery_id": delivery.id,
            },
        )

        logger.info(f"Sending SMS to client {client.email}")
