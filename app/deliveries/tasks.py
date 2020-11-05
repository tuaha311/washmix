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
@dramatiq.actor(periodic=cron("00 06 * * *"))
def create_recurring_request_every_day():
    now = localtime()
    weekday = now.isoweekday()

    for schedule in Schedule.objects.all():
        client = schedule.client
        address = client.main_address

        if not address:
            continue

        if weekday not in schedule.days:
            continue

        if schedule.status != settings.ACTIVE:
            continue

        key = f"recurring_schedule:{schedule.pk}"
        if exists_in_execution_cache(key):
            continue

        logger.info(f"Start of handling schedule # {schedule.pk}")

        service = RequestService(client=client)
        request, _ = service.get_or_create(
            extra_query={"schedule": schedule, "address": address},
            extra_defaults={
                "comment": schedule.comment,
                "is_rush": schedule.is_rush,
            },
        )

        add_to_execution_cache(key)

        logger.info(f"Created delivery # {request.pk}")
        logger.info(f"End of handling schedule # {schedule.pk}")
