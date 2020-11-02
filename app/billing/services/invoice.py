from django.conf import settings

from billing.models import Invoice
from orders.models import Order
from users.models import Client


class InvoiceService:
    def __init__(self, client: Client):
        self._client = client

    def update_or_create(
        self,
        order: Order,
        amount: int,
        purpose: str,
        discount: int = settings.DEFAULT_ZERO_DISCOUNT,
    ):
        invoice, _ = Invoice.objects.update_or_create(
            client=self._client,
            order=order,
            defaults={"amount": amount, "discount": discount, "purpose": purpose,},
        )

        return invoice

    @classmethod
    def update_invoice(cls, invoice, is_save_card: bool) -> Invoice:
        invoice.is_save_card = is_save_card
        invoice.save()

        return invoice
