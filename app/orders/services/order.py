from django.db.transaction import atomic

from billing.services.invoice import InvoiceService
from orders.models import Order
from orders.services import delivery, discount, extras
from orders.services.basket import BasketService
from users.models import Client


class OrderService:
    def __init__(self, client: Client):
        self._client = client
        self._delivery_service = delivery.DeliveryService(client)
        self._discount_service = discount.DiscountService(client)
        self._extras_service = extras.ExtrasService(client)
        self._invoice_service = InvoiceService(self._client)
        self._basket_service = BasketService(self._client)

    def checkout(self):
        basket = self._basket_service.basket

        with atomic():
            invoice = self._invoice_service.get_or_create(basket.amount)
            order = Order.objects.create(client=self._client, invoice=invoice, basket=basket,)

    @property
    def delivery(self):
        return self._delivery_service.delivery

    @property
    def discounts(self):
        return self._discount_service.discounts

    @property
    def extras(self):
        return self._extras_service.extras
