import logging
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from billing.utils import add_money_to_balance
from core.utils import add_to_execution_cache, convert_cent_to_dollars, exists_in_execution_cache
from notifications.tasks import send_email
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
        client_id = client.id
        recipient_list = [*settings.ADMIN_EMAIL_LIST, client.email]
        delta_days = (now - client.created).days

        if delta_days == 0:
            continue

        # 0 % 90 == 0
        if delta_days % credit_back_period != 0:
            continue

        key = f"credit_back_for_client:{client.pk}"
        if exists_in_execution_cache(key):
            continue

        logger.info(f"Start of accruing credit back for client {client.email}")

        order_list = client.order_list.filter(created__gte=moment_of_3_month_ago)
        order_container_list = [OrderContainer(item) for item in order_list]
        total_credit_back = sum(item.credit_back for item in order_container_list)

        if total_credit_back == 0:
            continue

        transaction = add_money_to_balance(client, total_credit_back, note="Credit Back by WashMix")

        client.refresh_from_db()
        dollar_credit_back = convert_cent_to_dollars(total_credit_back)
        dollar_balance = client.dollar_balance

        send_email.send(
            event=settings.ACCRUE_CREDIT_BACK,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
                "dollar_credit_back": dollar_credit_back,
                "dollar_balance": dollar_balance,
                "old_balance": convert_cent_to_dollars(
                    int(transaction.invoice.order.balance_before_purchase)
                ),
                "new_balance": convert_cent_to_dollars(
                    int(transaction.invoice.order.balance_after_purchase)
                ),
            },
        )

        add_to_execution_cache(key)

        logger.info(f"Credit back amount in $ {dollar_credit_back} for {client.email} was accrued")
        logger.info(f"End of accruing credit back for client {client.email}")
