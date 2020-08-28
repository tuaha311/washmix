from billing.models import Invoice
from users.models import Client


class PackageHandler:
    def __init__(self, client: Client):
        self._client = client

    def change(self, package):
        # TODO получать последний инвойс, который был не оплачен
        # TODO рефактор запроса last, create на get_or_create
        invoice = self._client.invoice_list.last()

        if not invoice:
            invoice = Invoice.objects.create(
                client=self._client, entity=package, amount=package.price,
            )
        else:
            invoice.object = package
            invoice.amount = package.price
            invoice.save()

        return invoice
