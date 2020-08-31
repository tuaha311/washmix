from billing.models import Invoice, Package, Subscription
from users.models import Client


class CheckoutHelper:
    def __init__(self, client: Client):
        self._client = client

    def checkout(self, package: Package, invoice: Invoice):
        subscription = Subscription.objects.create_and_fill(package, invoice)

        self._client.subscription = subscription
        self._client.save()
