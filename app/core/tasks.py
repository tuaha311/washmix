import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from archived.models import ArchivedCustomer
from core.utils import get_time_delta_for_promotional_emails
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery, Request
from notifications.tasks import send_email
from settings.base import (
    DELETE_USER_AFTER_TIMEDELTA,
    UNPAID_ORDER_FIRST_REMINDER_HOURS_TIMEDELTA,
    UNPAID_ORDER_SECOND_REMINDER_HOURS_TIMEDELTA,
    UNPAID_ORDER_TOTAL_REMINDER_EMAILS,
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
            
            next_promo_schedule = get_time_delta_for_promotional_emails(0)

            ArchivedCustomer.objects.get_or_create(
                email=user.email,
                defaults={
                    "phone": phone,
                    "full_name": full_name,
                    "address": address,
                    "zip_code": zip_code,
                    "promo_emails_sent_count": 0,
                    "next_promo_email_schedule": next_promo_schedule,
                },
            )
            recipient_list = [client.email]

            send_email(
                event=settings.FIRST_ARCHIVE_FOLLOW_UP,
                recipient_list=recipient_list,
            )
            user.delete()


@dramatiq.actor(periodic=cron("*/10 * * * *"))
def archive_periodic_promotional_emails():
    email_customers = ArchivedCustomer.objects.all()

    current_time = localtime()

    for client in email_customers:
        if client.next_promo_email_schedule is None:
            email_time = get_time_delta_for_promotional_emails(
                0
            )  # should return localtime() + 1 hour
            client.promo_emails_sent_count = 0
            client.next_promo_email_schedule = email_time
        else:
            email_time = client.next_promo_email_schedule

        sent_count = client.promo_emails_sent_count

        # Sending Email
        if email_time.strftime("%Y-%m-%d %H:00:00") == current_time.strftime("%Y-%m-%d %H:00:00"):
            if not sent_count or sent_count == 0:
                email_to_send = settings.FIRST_ARCHIVE_FOLLOW_UP
            elif sent_count == 1:
                email_to_send = settings.SECOND_ARCHIVE_FOLLOW_UP
            else:
                email_to_send = settings.THIRD_ARCHIVE_FOLLOW_UP

            recipient_list = [client.email]

            send_email(
                event=email_to_send,
                recipient_list=recipient_list,
            )

            client.increase_promo_emails_sent_count()

            if sent_count == 0:
                time_to_add = timedelta(hours=24)
            elif sent_count == 1:
                time_to_add = timedelta(weeks=1)
            elif sent_count == 2:
                time_to_add = timedelta(days=30)
            else:
                time_to_add = timedelta(days=90)

            email_schedule = (
                current_time.replace(hour=17, minute=0, second=0, microsecond=0) + time_to_add
            )

            client.next_promo_email_schedule = email_schedule

            client.save()
            print("PROMO EMAIL SENT TO " + client.email)
        else:
            print("Time did not match   ", client.email)


# every Hour at 0th Minute
@dramatiq.actor(periodic=cron("*/5 * * * *"))
def unpaid_orders_reminder_emails_setter():
    print("")
    print("STARTING THE PROCESS OF UNPAID ORDER SETUP")
    print("")
    # Get the all the request ids that are picked up
    pickup_request_ids = Delivery.objects.filter(
        kind__iexact=DeliveryKind.PICKUP,
        status__iexact=DeliveryStatus.COMPLETED,
    ).values_list("request_id", flat=True)

    # Fetch the orders that meet the specified criteria
    requests_without_order = Request.objects.filter(
        id__in=pickup_request_ids,
        order__isnull=True,
        unpaid_reminder_email_count__lte=0,
        unpaid_reminder_email_time__isnull=True,
    )

    print("LOCAL TIME:     ", localtime())
    reminder_time = localtime() + timedelta(minutes=2)
    print("REMINDER TIME:    ", reminder_time)
    print("")
    for request in requests_without_order:
        request.unpaid_reminder_email_time = reminder_time
        print("REQUEST SAVED:    ", request.pk)
        request.save()


@dramatiq.actor(periodic=cron("*/5 * * * *"))
def send_unpaid_order_reminder_emails():
    print("")
    print("STARTING THE PROCESS OF UNPAID ORDER EMAILS")
    print("")

    # Get the all the request ids that are picked up
    pickup_request_ids = Delivery.objects.filter(
        kind__iexact=DeliveryKind.PICKUP,
        status__iexact=DeliveryStatus.COMPLETED,
    ).values_list("request_id", flat=True)

    print("REQUEST IDS:    ", pickup_request_ids)
    # Fetch the orders that meet the specified criteria
    requests_without_order = Request.objects.filter(
        id__in=pickup_request_ids,
        order__isnull=True,
        unpaid_reminder_email_count__lte=UNPAID_ORDER_TOTAL_REMINDER_EMAILS,
        unpaid_reminder_email_time__isnull=False,
    )

    for request in requests_without_order:
        delivery = request.delivery_list.get(kind=DeliveryKind.PICKUP)
        email_time = request.unpaid_reminder_email_time
        current_time = localtime()
        if email_time <= current_time:
            print("Matching....    ", request.__dict__)
            recipient_list = settings.ADMIN_EMAIL_LIST

            full_name = request.client.full_name
            try:
                main_phone = request.client.main_phone.number
            except:
                main_phone = ""
            try:
                billing_address = request.client.billing_address["address_line_1"]
            except:
                billing_address = ""

            send_email(
                event=settings.UNCHARGED_ORDER_REMINDER,
                recipient_list=recipient_list,
                extra_context={
                    "full_name": full_name,
                    "main_phone": main_phone,
                    "billing_address": billing_address,
                    "client": request.client,
                    "request": request,
                    "delivery": delivery,
                },
            )

            request.unpaid_reminder_email_count += 1
            reminder_time = localtime() + timedelta(minutes=5)
            request.unpaid_reminder_email_time = reminder_time
            print("SAVING THE NEXT EMAIL TIME:     ", reminder_time)
            request.save()


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
