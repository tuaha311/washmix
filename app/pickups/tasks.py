import logging

from django.conf import settings
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from pickups.models import Schedule
from pickups.services.delivery import DeliveryService

logger = logging.getLogger(__name__)


# every day at 06:00
@dramatiq.actor(periodic=cron("00 06 * * *"))
def create_recurring_delivery_every_day():
    # TODO добавить идемпотентность

    now = localtime()
    weekday = now.isoweekday()

    for schedule in Schedule.objects.all():
        client = schedule.client

        # client doesn't have an address - we don't know a location of delivery
        if not client.main_address:
            continue

        if weekday not in schedule.days:
            continue

        if schedule.status != settings.ACTIVE:
            continue

        logger.info(f"Start of handling schedule # {schedule.pk}")

        service = DeliveryService(client=client, address=client.main_address,)
        delivery, _ = service.get_or_create(
            extra_query={"schedule": schedule,},
            extra_defaults={"comment": schedule.comment, "is_rush": schedule.is_rush,},
        )

        logger.info(f"Created delivery # {delivery.pk}")
        logger.info(f"End of handling schedule # {schedule.pk}")
