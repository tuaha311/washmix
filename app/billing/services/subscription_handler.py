from django.db.transaction import atomic

from billing.models import Invoice, Package, Subscription
from users.models import Client

DEFAULT_DISCOUNT = 0


class SubscriptionHandler:
    def __init__(self, client: Client):
        self._client = client

    def change(self, package: Package):
        # invoice without transaction by default not paid
        # and we are looking for them
        invoice = self._client.invoice_list.filter(transaction__isnull=True).last()

        with atomic():
            if not invoice:
                invoice = Invoice.objects.create(amount=package.price, discount=DEFAULT_DISCOUNT,)
            else:
                invoice.amount = package.price
                invoice.discount = DEFAULT_DISCOUNT
                invoice.save()

            # here we binding subscription and invoice
            Subscription.objects.create_and_fill(package, invoice)

        return invoice
