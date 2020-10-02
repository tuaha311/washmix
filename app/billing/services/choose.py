from django.db.models import ObjectDoesNotExist
from django.db.transaction import atomic

from billing.models import Invoice, Package, Subscription
from users.models import Client

DEFAULT_DISCOUNT = 0


class ChooseService:
    def __init__(self, client: Client):
        self._client = client

    def choose(self, package: Package):
        # invoice without transaction by default not paid
        # and we are looking for them
        invoice = self._client.invoice_list.filter(transaction__isnull=True).last()

        with atomic():
            if not invoice:
                invoice = Invoice.objects.create(
                    amount=package.price, discount=DEFAULT_DISCOUNT, client=self._client,
                )
            else:
                invoice.amount = package.price
                invoice.discount = DEFAULT_DISCOUNT
                invoice.save()

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
