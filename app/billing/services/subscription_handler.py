from django.db.transaction import atomic

from billing.models import Invoice, Subscription
from users.models import Client

DEFAULT_DISCOUNT = 0


class SubscriptionHandler:
    def __init__(self, client: Client):
        self._client = client

    def change(self, package):
        # TODO получать последний инвойс, который был не оплачен
        # TODO рефактор запроса last, create на get_or_create
        invoice = self._client.invoice_list.last()

        with atomic():
            if not invoice:
                invoice = Invoice.objects.create(
                    entity=package, amount=package.price, discount=DEFAULT_DISCOUNT,
                )
            else:
                invoice.subscription = package
                invoice.amount = package.price
                invoice.discount = DEFAULT_DISCOUNT
                invoice.save()

            subscription = Subscription.objects.create_and_fill(package, invoice)

            self._client.subscription = subscription
            self._client.save()

        return invoice
