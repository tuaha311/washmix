from billing.models import Invoice
from orders.services import delivery, discount, extras
from users.models import Client


class OrderService:
    def __init__(self, client: Client):
        self._client = client
        self._delivery_service = delivery.DeliveryService(client)
        self._discount_service = discount.DiscountService(client)
        self._extras_service = extras.ExtrasService(client)

    def checkout(self, invoice):
        pass

    @property
    def delivery(self):
        return self._delivery_service.delivery

    @property
    def discounts(self):
        return self._discount_service.discounts

    @property
    def extras(self):
        return self._extras_service.extras
