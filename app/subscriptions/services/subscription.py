from typing import Optional

from django.conf import settings
from django.db.models import ObjectDoesNotExist
from django.db.transaction import atomic

from billing.models import Invoice
from billing.services.invoice import InvoiceService
from subscriptions.models import Package, Subscription
from users.models import Client


class SubscriptionService:
    def __init__(self, client: Client):
        self._client = client

    def set_subscription(self, invoice: Invoice) -> Optional[Subscription]:
        """
        Final method that sets subscription on client after payment (checkout).
        """

        subscription = invoice.subscription

        # if invoice not paid - we can handle only PAYC subscription
        # if invoice paid - we can handle anything
        if not invoice.is_paid and subscription.name != settings.PAYC:
            return None

        with atomic():
            if invoice.is_save_card:
                invoice.card = self._client.main_card
                invoice.save()

            self._client.subscription = subscription
            self._client.save()

        return subscription

    def clone_from_package(self, package: Package):
        """
        Method helps to clone subscription based on package.
        It copies all fields from package to subscription.
        """

        package = package
        invoice_service = InvoiceService(self._client)

        with atomic():
            invoice = invoice_service.get_or_create(package.price)

            # here we creating or receiving subscription container
            # and in later steps we will bind it with invoice
            try:
                instance = invoice.subscription
            except ObjectDoesNotExist:
                instance = Subscription()

            subscription = Subscription.objects.fill_subscription(package, instance)
            subscription.invoice = invoice
            subscription.save()

        return invoice
