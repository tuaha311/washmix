from django.conf import settings

from billing.models import Invoice
from users.models import Client


class InvoiceService:
    def __init__(self, client: Client):
        self._client = client

    def create(self, amount: int, purpose: str, discount: int = settings.DEFAULT_ZERO_DISCOUNT):
        invoice = Invoice.objects.create(
            amount=amount, discount=discount, client=self._client, purpose=purpose,
        )

        return invoice

    def get_or_create(
        self, amount: int, purpose: str, discount: int = settings.DEFAULT_ZERO_DISCOUNT
    ):
        # invoice without transaction by default not paid
        # and we are looking for them
        invoice = self._client.invoice_list.filter(transaction__isnull=True, purpose=purpose).last()

        if not invoice:
            invoice = Invoice.objects.create(
                amount=amount, discount=discount, client=self._client, purpose=purpose,
            )

        else:
            invoice.amount = amount
            invoice.discount = discount
            invoice.save()

        return invoice

    @classmethod
    def update_invoice(cls, invoice, is_save_card: bool) -> Invoice:
        invoice.is_save_card = is_save_card
        invoice.save()

        return invoice
