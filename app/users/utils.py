from datetime import timedelta
from billing.choices import InvoiceProvider
from billing.models.transaction import Transaction
from users.models import Client
from django.db.models import Q
from django.db.models import Prefetch
from django.utils.timezone import localtime


# This is an one time script which will set schedule promotional SMS to all clients
def schedule_promo_sms_notification():
    batch_size = 50
    clients_queryset = Client.objects.filter(promo_sms_notification=None)
    clients_count = clients_queryset.count()
    schedule_date = localtime().date()

    for offset in range(0, clients_count, batch_size):
        clients_batch = clients_queryset[offset:offset + batch_size]

        for cl in clients_batch:
            cl.promo_sms_notification = schedule_date
            cl.save()

        schedule_date += timedelta(days=1)


def users_with_scheduled_promotional_sms(start_date, current_date, cash_back_within):

    # Update promo_sms_notification for users
    Client.objects.filter(
        Q(promo_sms_notification__lte=current_date, order_list__created__gte=start_date)
    ).update(promo_sms_notification=current_date + timedelta(days=30))

    # Query for users with scheduled promotional SMS for the current date
    return (
        Client.objects.filter(
            Q(promo_sms_notification__lte=current_date)
        ).exclude(
            Q(order_list__created__gte=start_date) #Excluding Clients who have placed order in given range
        )
        .distinct("user_id")
        .prefetch_related( #Eager loading for cash back transactions
            "transaction_list",
            Prefetch(
                "transaction_list",
                queryset=Transaction.objects.filter(
                    provider=InvoiceProvider.CREDIT_BACK, created__range=(cash_back_within, current_date)
                ).order_by("-created"),
                to_attr="credit_back_transactions",
            ),
        )
    )
