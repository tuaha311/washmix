import logging

from django.conf import settings
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from core.utils import add_to_execution_cache, exists_in_execution_cache
from deliveries.models import Schedule
from deliveries.services.requests import RequestService

logger = logging.getLogger(__name__)


# every day at 06:00
@dramatiq.actor(
    periodic=cron("*/5 * * * *"),
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
