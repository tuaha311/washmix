import datetime
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.timezone import localtime

import dramatiq
from periodiq import cron

from archived.models import ArchivedCustomer
from core.utils import get_time_delta_for_promotional_emails
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery
from notifications.tasks import send_email, send_sms
from orders.choices import OrderPaymentChoices, OrderStatusChoices
from orders.models import Order
from settings.base import (
    DELETE_USER_AFTER_TIMEDELTA,
    SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
    UNPAID_ORDER_FIRST_REMINDER_HOURS_TIMEDELTA,
    UNPAID_ORDER_SECOND_REMINDER_HOURS_TIMEDELTA,
    UNPAID_ORDER_TOTAL_REMINDER_EMAILS,
)
from subscriptions.utils import is_advantage_program
from users.models import Client

logger = logging.getLogger(__name__)


# every hour every 15 minutes
@dramatiq.actor(periodic=cron("*/15 * * * *"))
def periodic_scheduler_health():
    """
    Check for scheduler that he is alive.
    """

    logger.info("Periodic scheduler health - OK")


# every 5 minutes
@dramatiq.actor(periodic=cron("*/5 * * * *"))
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
                        + get_time_delta_for_promotional_emails(settings.PROMO_EMAIL_PERIODS, 0, settings.TOTAL_PROMOTIONAL_EMAIL_COUNT)
                    ),
                },
            )
            user.delete()

#@dramatiq.actor(periodic=cron("0 23 * * 6"))
# every week on Saturday 11 PM
@dramatiq.actor(periodic=cron("*/1 * * * *"))
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


# every 1 minutes
@dramatiq.actor(periodic=cron("*/1 * * * *"))
def archive_periodic_promotional_emails():
    email_customers = ArchivedCustomer.objects.filter(
        promo_email_sent_count__lt=settings.TOTAL_PROMOTIONAL_EMAIL_COUNT
    )

    current_time = localtime()

    for client in email_customers:
        print(client.promo_email_sent_count)
        if client.promo_email_send_time is None:
            email_time = current_time
            client.promo_email_send_time = current_time
            client.save()
        else:
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
                settings.PROMO_EMAIL_PERIODS,
                client.promo_email_sent_count,
                settings.TOTAL_PROMOTIONAL_EMAIL_COUNT
            )
            client.set_next_promo_email_send_date(time_to_add)
            client.save()
            print("PROMO EMAIL SEND To " + client.email)

# Check Sms Sending Criteraia Daily
# @dramatiq.actor(periodic=cron("*/59 * * * *"))
# Every Hour
@dramatiq.actor(periodic=cron("*1 * * * *"))
def send_reminder_service_text():
    signed_up_users_with_no_orders_at_all = Client.objects.filter(
        Q(
            created__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
            order_list__isnull=True,
            promo_sms_sent__isnull=True,
        )
        | Q(
            created__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
            order_list__isnull=True,
            promo_sms_sent__isnull=False,
            promo_sms_sent__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
        )
    ).distinct("user_id")[:20]

    users_with_no_orders_within_given_limit = Client.objects.filter(
        Q(
            order_list__changed__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
            order_list__status__exact=OrderStatusChoices.COMPLETED,
            promo_sms_sent__isnull=True,
        )
        | Q(
            order_list__changed__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
            order_list__status__exact=OrderStatusChoices.COMPLETED,
            promo_sms_sent__isnull=False,
            promo_sms_sent__lt=localtime() - SERVICE_REMINDER_SMS_DURATION_DAYS_TIMEDELTA,
        )
    ).distinct("user_id")[:20]

    if signed_up_users_with_no_orders_at_all:
        for client in signed_up_users_with_no_orders_at_all:
            send_sms.send_with_options(
                kwargs={
                    "event": settings.SERVICE_PROMOTION,
                    "recipient_list": [client.main_phone.number],
                },
                delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
            )
            client.set_promo_sms_sent_date(localtime())
            client.save()
            logger.info(f"Sendin SMS to client {client.email}")

    if users_with_no_orders_within_given_limit:
        for client in users_with_no_orders_within_given_limit:
            send_sms.send_with_options(
                kwargs={
                    "event": settings.SERVICE_PROMOTION,
                    "recipient_list": [client.main_phone.number],
                },
                delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
            )
            client.set_promo_sms_sent_date(localtime())
            client.save()
            logger.info(f"Sendin SMS to client {client.email}")


# every Hour at 1st Minute
@dramatiq.actor(periodic=cron("*/1 * * * *"))
def unpaid_orders_reminder_emails_setter():
    request_ids = Delivery.objects.filter(
        kind__iexact=DeliveryKind.PICKUP,
        status__iexact=DeliveryStatus.COMPLETED,
    ).values_list("request_id", flat=True)
    if request_ids.exists():
        reminding_orders = Order.objects.filter(
            status__iexact=OrderStatusChoices.ACCEPTED,
            payment__iexact=OrderPaymentChoices.UNPAID,
            unpaid_reminder_email_count__lte=0,
            unpaid_reminder_email_time__isnull=True,
            request_id__in=request_ids,
        )
        for order in reminding_orders:
            order.set_unpaid_order_reminder_email_time(
                localtime() + UNPAID_ORDER_FIRST_REMINDER_HOURS_TIMEDELTA
            )
            order.save()


# every Hour at 1st Minute
@dramatiq.actor(periodic=cron("*/1 * * * *"))
def send_unpaid_order_reminder_emails():
    request_ids = Delivery.objects.filter(
        kind__iexact=DeliveryKind.PICKUP,
        status__iexact=DeliveryStatus.COMPLETED,
    ).values_list("request_id", flat=True)
    if request_ids.exists():
        reminding_orders = Order.objects.filter(
            status__iexact=OrderStatusChoices.ACCEPTED,
            payment__iexact=OrderPaymentChoices.UNPAID,
            unpaid_reminder_email_count__lt=UNPAID_ORDER_TOTAL_REMINDER_EMAILS,
            unpaid_reminder_email_time__isnull=False,
            request_id__in=request_ids,
        )
        for order in reminding_orders:
            email_time = order.unpaid_order_reminder_email_time
            current_time = localtime()
            if email_time.strftime("%Y-%m-%d %H:00:00") == current_time.strftime(
                "%Y-%m-%d %H:00:00"
            ):
                order = Order.objects.get(id=order.pk)
                subscription = order.client.subscription
                is_advantage = is_advantage_program(subscription.name)

                recipient_list = settings.ADMIN_EMAIL_LIST
                send_email(
                    event=settings.UNCHARGED_ORDER_REMINDER,
                    recipient_list=recipient_list,
                    extra_context={
                        "client_id": order.client.id,
                        "order_id": order.pk,
                        "is_advantage": is_advantage,
                    },
                )
                order.increase_unpaid_reminder_email_count()
                if not order.unpaid_reminder_email_count:
                    order.set_unpaid_order_reminder_email_time(
                        email_time + UNPAID_ORDER_SECOND_REMINDER_HOURS_TIMEDELTA
                    )
                order.save()


@dramatiq.actor
def worker_health():
    """
    Check for worker that he is alive.
    """

    logger.info("Worker health - OK")
