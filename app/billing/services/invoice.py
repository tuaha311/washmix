from django.conf import settings
from django.db.models import Model

from users.models import Client


class InvoiceService:
    def __init__(self, client: Client):
        self._client = client

    def refresh_amount_discount(
        self, entity: Model, amount: int, discount: int = settings.DEFAULT_ZERO_DISCOUNT
    ):
        entity.amount = amount
        entity.discount = discount

        entity.save()

        return entity
