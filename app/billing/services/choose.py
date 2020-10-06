from django.db.models import ObjectDoesNotExist
from django.db.transaction import atomic

from billing.models import Package, Subscription
from billing.services.invoice import InvoiceService
from users.models import Client


class ChooseService:
    def __init__(self, client: Client, package: Package):
        self._client = client
        self._package = package

    def set_package(self):
        package = self._package
        invoice_service = InvoiceService(self._client)

        with atomic():
            invoice = invoice_service.get_or_create(self._package.price)

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
