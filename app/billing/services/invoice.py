from django.conf import settings
from django.db.models import Model

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
            purpose=purpose,
            defaults={"amount": amount, "discount": discount},
        )

        return invoice

    def refresh_amount_discount(
        self, entity: Model, amount: int, discount: int = settings.DEFAULT_ZERO_DISCOUNT
    ):
        entity.amount = amount
        entity.discount = discount

        entity.save()

        return entity
