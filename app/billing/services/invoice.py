from django.conf import settings

from billing.models import Invoice
from users.models import Client


class InvoiceService:
    def __init__(self, client: Client):
        self._client = client

    def get_or_create(self, amount: int):
        # invoice without transaction by default not paid
        # and we are looking for them
        invoice = self._client.invoice_list.filter(transaction__isnull=True).last()

        if not invoice:
            invoice = Invoice.objects.create(
                amount=amount, discount=settings.DEFAULT_DISCOUNT, client=self._client,
            )
        else:
            invoice.amount = amount
            invoice.discount = settings.DEFAULT_DISCOUNT
            invoice.save()

        return invoice
