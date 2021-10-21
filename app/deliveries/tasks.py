import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.utils.timezone import localtime

import dramatiq
import pytz
from periodiq import cron

from core.utils import add_to_execution_cache, exists_in_execution_cache
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery, Schedule
from deliveries.services.requests import RequestService
from notifications.tasks import send_sms

logger = logging.getLogger(__name__)


# every day at 06:00
@dramatiq.actor(
    periodic=cron("00 06 * * *"),
    max_retries=settings.DRAMATIQ_MAX_RETRIES,
    max_age=settings.DRAMATIQ_MAX_AGE,
)
def create_recurring_request_every_day():
    now = localtime()
    weekday = now.isoweekday()

    for schedule in Schedule.objects.all():
        client = schedule.client
        address = client.main_address

        if not address:
            logger.info(f"Schedule # {schedule.pk} doesn't have a address")
            continue

        if weekday not in schedule.days:
            logger.info(f"Schedule # {schedule.pk} doesn't include this weekday {weekday}")
            continue

        if schedule.status != settings.ACTIVE:
            logger.info(f"Schedule # {schedule.pk} not active")
            continue

        key = f"recurring_schedule:{schedule.pk}"
        if exists_in_execution_cache(key):
            logger.info(f"Request for schedule # {schedule.pk} already handled")
            continue

        logger.info(f"Start of handling schedule # {schedule.pk}")

        service = RequestService(client=client)
        request = service.create(
            schedule=schedule,
            address=address,
            comment=schedule.comment,
            is_rush=schedule.is_rush,
        )

        add_to_execution_cache(key)

        logger.info(f"Created delivery # {request.pk}")
        logger.info(f"End of handling schedule # {schedule.pk}")


@dramatiq.actor(
    periodic=cron("00 06 * * *"),
    max_retries=settings.DRAMATIQ_MAX_RETRIES,
    max_age=settings.DRAMATIQ_MAX_AGE,
)
def send_sms_if_pickup_due_tomorrow():
    pst = pytz.timezone("America/Los_Angeles")

    for delivery in Delivery.objects.filter(
        kind=DeliveryKind.PICKUP, status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.IN_PROGRESS]
    ):
        client = delivery.request.client
        number = client.main_phone.number
        is_pickup = delivery.kind == DeliveryKind.PICKUP

        if delivery.date - timedelta(days=1) != localtime().date():
            logger.info(f"Delivery # {delivery.pk} pickup not due for tomorrow")
            continue

        key = f"pickup_schedule:{delivery.pk}"
        if exists_in_execution_cache(key):
            logger.info(f"Notification for delivery # {delivery.pk} already handled")
            continue

        logger.info(f"Start of handling notification for delivery # {delivery.pk}")

        send_sms.send_with_options(
            kwargs={
                "event": settings.PICKUP_DUE_TOMORROW,
                "recipient_list": [number],
                "extra_context": {
                    "client_id": client.id,
                    "delivery_id": delivery.id,
                },
            },
            delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
        )

        logger.info(f"Sending SMS to client {client.email}")

        add_to_execution_cache(key)

        logger.info(f"End of handling delivery notification for # {delivery.pk}")
