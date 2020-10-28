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

    @classmethod
    def update_invoice(cls, invoice, is_save_card: bool) -> Invoice:
        invoice.is_save_card = is_save_card
        invoice.save()

        return invoice
