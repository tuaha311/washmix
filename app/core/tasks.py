import logging

from django.contrib.auth import get_user_model
from django.utils.timezone import localtime

from datetime import timedelta
import dramatiq
from periodiq import cron

from archived.models import ArchivedCustomer
from settings.base import (
    DELETE_USER_AFTER_TIMEDELTA,
    ARCHIVE_CUSTOMER_FIRST_PROMOTION_EMAIL_SEND_HOURS_TIMEDELTA,
    TOTAL_PROMOTIONAL_EMAIL_COUNT
)
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
                    "promo_email_send_time": (localtime() + ARCHIVE_CUSTOMER_FIRST_PROMOTION_EMAIL_SEND_HOURS_TIMEDELTA)
                },
            )

            user.delete()


@dramatiq.actor(periodic=cron("0 23 * * 6"))
def delete_archived_customers_who_signed_up_already():
    """
    Deleting All Previous Users Who have signed up, but were not deleted.
    """
    user = get_user_model()
    delete_clients = ArchivedCustomer.objects.filter(
        email__in=user.objects.values_list("email", flat=True)
    )
    for client in delete_clients:
        client.delete()


# every 10 minutes
@dramatiq.actor(periodic=cron("*/10 * * * *"))
def archive_periodic_promotional_emails():
    email_customers = ArchivedCustomer.objects.filter(promo_email_sent_count__lt = TOTAL_PROMOTIONAL_EMAIL_COUNT)
    currentTime = localtime()
    for client in email_customers:
        email_time = client.promo_email_send_time
        sent_count = client.promo_email_sent_count
        # Sending First Email
        if not sent_count and ( email_time.strftime('%Y-%m-%d %H:00:00') == currentTime.strftime('%Y-%m-%d %H:00:00') ) :

        elif sent_count and (email_time.date() == currentTime.date()) :
            print("ELIF")

@dramatiq.actor
def worker_health():
    """
    Check for worker that he is alive.
    """

    logger.info("Worker health - OK")
