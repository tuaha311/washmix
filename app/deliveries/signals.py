import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from deliveries.choices import DeliveryKind, DeliveryStatus
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
    delivery_id = delivery.id
    client = delivery.client
    main_phone = client.main_phone

    if not main_phone:
        return None

    # when Delivery created from Admin Panel - it triggers signal 2 times:
    # 1. with Delivery without ID
    # 2. with created Delivery with ID (only this case is valid)
    if not delivery_id:
        return None

    number = main_phone.number
    is_created = created
    is_date_updated = False
    is_dropoff = delivery.kind == DeliveryKind.DROPOFF
    is_pickup = delivery.kind == DeliveryKind.PICKUP
    is_completed = delivery.status == DeliveryStatus.COMPLETED
    is_cancelled = delivery.status == DeliveryStatus.CANCELLED

    if update_fields:
        is_date_updated = "date" in update_fields

    if is_pickup and (is_created or is_date_updated):
        # we are adding some delay to wait for database
        # transaction commit

        send_sms.send_with_options(
            kwargs={
                "event": settings.NEW_DELIVERY,
                "recipient_list": [number],
                "extra_context": {
                    "client_id": client.id,
                    "delivery_id": delivery.id,
                },
            },
            delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
        )

        logger.info(f"Sending SMS to client {client.email}")

    if is_dropoff and is_completed:
        # we are adding some delay to wait for database
        # transaction commit
        send_sms.send_with_options(
            kwargs={
                "event": settings.DELIVERY_DROPOFF_COMPLETE,
                "recipient_list": [number],
                "extra_context": {
                    "client_id": client.id,
                    "delivery_id": delivery.id,
                },
            },
            delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
        )

        logger.info(f"Sending SMS to client {client.email}")

    if is_pickup and is_cancelled:
        send_sms.send_with_options(
            kwargs={
                "event": settings.PICKUP_REQUEST_CANCELED,
                "recipient_list": [number],
                "extra_context": {
                    "client_id": client.id,
                    "delivery_id": delivery.id,
                },
            },
            delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
        )

        logger.info(f"Sending SMS to client {client.email}")

    if is_pickup and is_completed:
        send_sms.send_with_options(
            kwargs={
                "event": settings.ORDER_PICKUP_COMPLETE,
                "recipient_list": [number],
                "extra_context": {
                    "client_id": client.id,
                    "delivery_id": delivery.id,
                },
            },
            delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
        )

        logger.info(f"Sending SMS to client {client.email}")
