import logging

from django.contrib.auth import get_user_model
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from archived.models import ArchivedCustomer
from notifications.tasks import send_email, send_sms
from orders.choices import OrderStatusChoices
from orders.models import Order
from settings.base import DELETE_USER_AFTER_TIMEDELTA
from users.models import Client

logger = logging.getLogger(__name__)


# every hour every 15 minutes
@dramatiq.actor(periodic=cron("*/15 * * * *"))
def periodic_scheduler_health():
    """
    Check for scheduler that he is alive.
    """

    logger.info("Periodic scheduler health - OK")


# every 10 minutes
@dramatiq.actor(periodic=cron("*/10 * * * *"))
def archive_not_signedup_users():
    """
    Deleting the users that were unable to signup after 6 hours of user creation
    Moving the user to archived user table in archived app
    """
    delete_clients = Client.objects.filter(
        card_list__isnull=True, created__lt=localtime() - DELETE_USER_AFTER_TIMEDELTA
    )
    print("************* IN archive_not_signedup_users *************")
    delete_clients_count = delete_clients.count()
    print(f"Total delete clients: {delete_clients_count}")
    if delete_clients:
        for client in delete_clients:
            phone = ""
            full_name = ""
            address = ""
            zip_code = ""

            user = client.user
            if client.main_phone:
                phone = client.main_phone.number
            if client.main_address:
                address = (
                    f"{client.main_address.address_line_1} {client.main_address.address_line_2}"
                )
                zip_code = client.main_address.zip_code.value
            if user.first_name:
                full_name = f"{user.first_name} {user.last_name}"

            ArchivedCustomer.objects.get_or_create(
                email=user.email,
                defaults={
                    "phone": phone,
                    "full_name": full_name,
                    "address": address,
                    "zip_code": zip_code,
                },
            )

            user.delete()


@dramatiq.actor(periodic=cron("*/13 * * * *"))
def delete_archived_customers_who_signed_up_already():
    """
    Deleting All Previous Users Who have signed up, but were not deleted.
    """
    user = get_user_model()
    delete_clients = ArchivedCustomer.objects.filter(
        email__in=user.objects.values_list("email", flat=True)
    )
    print("************* IN delete_archived_customers_who_signed_up_already *************")
    delete_clients_count = delete_clients.count()
    print(f"Total delete clients: {delete_clients_count}")
    for client in delete_clients:
        client.delete()


@dramatiq.actor
def worker_health():
    """
    Check for worker that he is alive.
    """

    logger.info("Worker health - OK")
