from django.conf import settings
from django.db.models import F
from django.db.transaction import atomic

from rest_framework import serializers

from billing.models import Invoice
from billing.services.invoice import InvoiceService
from orders.models import Basket, Order, Price, Quantity
from orders.services.order import OrderService
from users.models import Client


class BasketService:
    def __init__(self, client: Client):
        self._client = client

    def validate(self, price: Price, count: int, action: str):
        quantity = self._get_or_create_quantity(price)

        if action == settings.BASKET_REMOVE and quantity.count < count:
            raise serializers.ValidationError(
                detail="You can't remove more items that in basket.",
                code="cant_perform_item_remove",
            )

    def add_item(self, price: Price, count: int) -> Basket:
        with atomic():
            quantity = self._get_or_create_quantity(price)

            quantity.count = F("count") + count
            quantity.save()

        return self.basket

    def remove_item(self, price: Price, count: int) -> Basket:
        with atomic():
            quantity = self._get_or_create_quantity(price)

            quantity.count = F("count") - count
            quantity.save()

            if quantity.count == 0:
                quantity.delete()

        return self.basket

    def clear_all(self):
        self.basket.item_list.set([])
        self.basket.save()

    def checkout(self):
        invoice_service = InvoiceService(self._client)
        order_service = OrderService(self._client)

        with atomic():
            invoice = invoice_service.get_or_create(self.basket.amount)
            order = order_service.checkout(invoice)

        return order

    @property
    def basket(self) -> Basket:
        basket, _ = Basket.objects.get_or_create(client=self._client, order__isnull=True,)
        return basket

    def _get_or_create_quantity(self, price: Price) -> Quantity:
        quantity, _ = Quantity.objects.get_or_create(
            basket=self.basket, price=price, defaults={"count": 0,},
        )
        return quantity
