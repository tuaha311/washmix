import datetime
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from archived.models import ArchivedCustomer
from core.utils import get_time_delta_for_promotional_emails
from notifications.tasks import send_email
from settings.base import DELETE_USER_AFTER_TIMEDELTA,SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA
from users.models import Client
from orders.models import Order
from orders.choices import OrderStatusChoices

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
    Deleting the users that were unable to signup after 3 hours of user creation
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
                    "promo_email_sent_count": 0,
                    "promo_email_send_time": (
                        localtime()
                        + get_time_delta_for_promotional_emails(settings.PROMO_EMAIL_PERIODS, 0)
                    ),
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
    email_customers = ArchivedCustomer.objects.filter(
        promo_email_sent_count__lt=settings.TOTAL_PROMOTIONAL_EMAIL_COUNT
    )
    current_time = localtime()
    for client in email_customers:
        email_time = client.promo_email_send_time
        sent_count = client.promo_email_sent_count
        # Sending Email
        if (
            not sent_count
            and (
                email_time.strftime("%Y-%m-%d %H:00:00")
                == current_time.strftime("%Y-%m-%d %H:00:00")
            )
        ) or (sent_count and (email_time.date() == current_time.date())):
            if not client.promo_email_sent_count:
                email_to_send = settings.FIRST_PROMOTION_EMAIL_ARCHIVE_CUSTOMER
            elif client.promo_email_sent_count == 1:
                email_to_send = settings.SECOND_PROMOTION_EMAIL_ARCHIVE_CUSTOMER
            else:
                email_to_send = settings.THIRD_PROMOTION_EMAIL_ARCHIVE_CUSTOMER
            send_email(
                event=email_to_send,
                recipient_list=[client.email],
                extra_context={
                    "date": datetime.datetime.now().strftime("%d-%B-%Y"),
                },
            )
            client.increase_promo_email_sent_count()
            time_to_add = get_time_delta_for_promotional_emails(
                settings.PROMO_EMAIL_PERIODS, client.promo_email_sent_count
            )
            client.set_next_promo_email_send_date(time_to_add)
            client.save()

# Check Sms Sending Criteraia Daily
# @dramatiq.actor(periodic=cron("*/10 * * * *"))
def send_reminder_service_text():
    # reminder_service_sms_clients = Client.objects.filter(
    #
    # )
    # signed_up_users_with_no_orders = Client.objects.filter(created__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,last_sms_sent__isnull=True).exclude(id__in=Order.objects.values('client'))

    # Clients Who Signed Up 2 months Ago But havent placed any order yet
    # signed_up_users_with_no_orders_at_all = Client.objects.filter(
    #     created__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
    #     last_sms_sent__isnull=True,
    #     order_list__isnull=True)
    signed_up_users_with_no_orders_at_all = Client.objects.filter(
        created__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
        last_sms_sent__isnull=True,
        order_list__isnull=True)

    users_with_no_orders_within_two_months = Client.objects.filter(
        order_list__created__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
        order_list__status__in=OrderStatusChoices.COMPLETED)

    print("Printing Users with NO ORDERS AT ALL")

    if signed_up_users_with_no_orders_at_all:
        for client in signed_up_users_with_no_orders_at_all:
            print(client.main_phone)
    send_sms.send_with_options(
        kwargs={
            "event": settings.NO_SHOW,
            "recipient_list": [str(client.main_phone)],
            },
        },
        delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
    )
    print("Printing Users with LAATEE ORDERS")
    if users_with_no_orders_within_two_months:
        for client in users_with_no_orders_within_two_months:
            print(client.__str__())



@dramatiq.actor
def worker_health():
    """
    Check for worker that he is alive.
    """

    logger.info("Worker health - OK")
