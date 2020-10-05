import logging
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from billing.utils import create_credit_back
from users.models import Client

logger = logging.getLogger(__name__)


@dramatiq.actor(periodic=cron("* * * * *"))
def periodic_worker_health():
    logger.info("OK")


# every day at 05:00
@dramatiq.actor(periodic=cron("00 05 * * *"))
def accrue_credit_back_every_3_month():
    # TODO добавить идемпотентность

    now = localtime()
    credit_back_period = settings.CREDIT_BACK_PERIOD
    moment_of_3_month_ago = now - timedelta(days=credit_back_period)

    for client in Client.objects.all():
        delta_days = (now - client.created).days
        subscription = client.subscription

        # if client doesn't have a subscription or subscription doesn't includes credit back
        # we are skip him
        if not subscription or not subscription.has_credit_back:
            continue

        # we are handling periodically clients every 3 month
        # after signup day
        if delta_days % credit_back_period != 0:
            continue

        logger.info(f"Start of accruing credit back for client {client.email}")

        # we are considering only orders, that was created 3 month ago
        order_list = client.order_list.filter(created__gte=moment_of_3_month_ago)
        amount = sum(item.amount for item in order_list)

        # if client doesn't have any orders - we are skip him
        if amount == 0:
            continue

        create_credit_back(client, amount)

        logger.info(f"Credit back amount in cents {amount} for {client.email} was accrued")
        logger.info(f"End of accruing credit back for client {client.email}")
