import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from billing.choices import InvoicePurpose
from billing.models import Invoice
from billing.services.payments import PaymentService
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery
from notifications.tasks import send_sms
from subscriptions.utils import is_advantage_program

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
    is_no_show = delivery.status == DeliveryStatus.NO_SHOW
    is_advantage = bool(client.subscription) and is_advantage_program(client.subscription.name)
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
    if is_pickup and is_no_show:
        amount = 1990
        if is_advantage:
            amount = 1490
        invoice = Invoice.objects.create(
            client=client,
            amount=amount,
            discount=settings.DEFAULT_ZERO_DISCOUNT,
            purpose=InvoicePurpose.ORDER,
        )
        payment_service = PaymentService(client, invoice)
        payment_service.charge()
        send_sms.send_with_options(
            kwargs={
                "event": settings.NO_SHOW,
                "recipient_list": [number],
                "extra_context": {
                    "client_id": client.id,
                    "delivery_id": delivery.id,
                },
            },
            delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
        )

        logger.info(f"Sending SMS to client {client.email}")
