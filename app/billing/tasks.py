from django.conf import settings
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from billing.utils import create_credit_back
from users.models import Client


@dramatiq.actor(periodic=cron("* * * * *"))
def hello():
    print("HELLO WORLD")


# every day at 05:00
@dramatiq.actor(periodic=cron("00 05 * * *"))
def accrue_credit_back_every_3_month():
    now = localtime()

    for client in Client.objects.all():
        delta_days = (now - client.created).days
        credit_back_period = settings.CREDIT_BACK_PERIOD
        subscription = client.subscription

        # if client doesn't have a subscription or subscription doesn't includes credit back
        # we are skip him
        if not subscription or not subscription.has_credit_back:
            continue

        # we are handling periodically clients every 3 month
        # after signup day
        if delta_days % credit_back_period != 0:
            continue

        order_list = client.order_list.all()
        amount = sum(item.amount for item in order_list)

        # if client doesn't have any orders - we are skip him
        if amount == 0:
            continue

        create_credit_back(client, amount)
