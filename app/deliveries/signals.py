import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver

from billing.choices import InvoiceProvider, InvoicePurpose
from billing.models.invoice import Invoice
from billing.utils import create_credit
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery
from notifications.tasks import send_admin_client_information, send_sms
from orders.choices import OrderPaymentChoices
from orders.models.order import Order
from orders.services.order import OrderService
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
    print("I AM ON SIGNALLLLL")
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
        print("111111111")
        # we are adding some delay to wait for database
        # transaction commit
        if is_date_updated:
            event = settings.UPDATED_DELIVERY
        else:
            event = settings.NEW_DELIVERY

        send_sms.send_with_options(
            kwargs={
                "event": event,
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
        print("22222222")
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
        print("3333333")
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
        print("4444444")
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
        print("555555")
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
        send_admin_client_information(client.id, "The customer did not show up for the Pickup")

        logger.info(f"Sending SMS to client {client.email}")

    if is_dropoff and is_no_show:
        print("6666666")
        delivery_request = delivery.request
        if not Order.objects.filter(request=delivery_request).exists():
            print("HERERERRERERERER")
            amount = 1990
            if is_advantage:
                amount = 1490
            with atomic():
                order_service = OrderService(client)
                order = order_service.prepare(delivery.request)
                order.note = "NO BAG OUTSIDE FOR PICKUP"
                order.save()
                print("ORDER:       ", order.__dict__)
                order, full_paid = order_service.checkout(order)
                if full_paid:
                    order_service.finalize(order, None, True)
