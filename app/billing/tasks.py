import logging
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from billing.utils import add_credits
from core.utils import add_to_execution_cache, exists_in_execution_cache
from orders.containers.order import OrderContainer
from users.models import Client

logger = logging.getLogger(__name__)


# every day at 05:00
@dramatiq.actor(
    periodic=cron("00 05 * * *"),
    max_retries=settings.DRAMATIQ_MAX_RETRIES,
    max_age=settings.DRAMATIQ_MAX_AGE,
)
def accrue_credit_back_every_3_month():
    now = localtime()
    credit_back_period = settings.CREDIT_BACK_PERIOD
    moment_of_3_month_ago = now - timedelta(days=credit_back_period)

    for client in Client.objects.all():
        delta_days = (now - client.created).days
        subscription = client.subscription

        if not subscription or not subscription.has_credit_back:
            continue

        if delta_days % credit_back_period != 0:
            continue

        key = f"credit_back_for_client:{client.pk}"
        if exists_in_execution_cache(key):
            continue

        logger.info(f"Start of accruing credit back for client {client.email}")

        order_list = client.order_list.filter(created__gte=moment_of_3_month_ago)
        order_container_list = [OrderContainer(item) for item in order_list]
        order_total_amount = sum(item.amount_with_discount for item in order_container_list)

        if order_total_amount == 0:
            continue

        credit_back_amount = order_total_amount * settings.CREDIT_BACK_PERCENTAGE / 100

        add_credits(client, credit_back_amount)

        add_to_execution_cache(key)

        logger.info(
            f"Credit back amount in cents {credit_back_amount} for {client.email} was accrued"
        )
        logger.info(f"End of accruing credit back for client {client.email}")
