from typing import List, Optional

from django.conf import settings
from django.db.models import F
from django.db.transaction import atomic

from rest_framework import serializers

from billing.choices import Purpose
from billing.models import Invoice
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from core.interfaces import PaymentInterfaceService
from orders.containers.basket import BasketContainer
from orders.containers.order import OrderContainer
from orders.models import Basket, Order, Price, Quantity
from users.models import Client

DEFAULT_COUNT = 0


class BasketService(PaymentInterfaceService):
    """
    This service is responsible for basket (card) business logic.
    Using this service you can:
        - Add items to basket
        - Remove items from basket
        - Clear basket
        - See items in basket
        - See discount for item
        - See total discount on your basket
    """

    def __init__(self, client: Client):
        self._client = client

    def create_invoice(
        self,
        order: Order,
        basket: Optional[Basket],
        **kwargs,
    ) -> Optional[List[Invoice]]:
        """
        Basket invoicing method, called when POS checkout occurs.
        """

        if not basket:
            return None

        client = self._client
        subscription = client.subscription
        invoice_service = InvoiceService(client)
        basket_container = BasketContainer(subscription, basket)

        basket_invoice = invoice_service.update_or_create(
            order=order,
            amount=basket_container.amount,
            discount=basket_container.discount,
            purpose=Purpose.BASKET,
        )
        basket.invoice = basket_invoice
        basket.save()

        return [basket_invoice]

    def charge(self, basket: Basket, **kwargs):
        """
        We are charging user for:
            - basket amount
            - pickup delivery amount
            - dropoff delivery amount
        """

        if not basket:
            return None

        client = self._client
        invoice = basket.invoice

        payment_service = PaymentService(client, invoice)
        payment_service.charge()

    def checkout(self, **kwargs):
        """
        Dummy implementation of interface.
        """
        pass

    def validate(self, order: Order, price: Price, count: int, action: str):
        """
        Makes all validation related stuff.
        """

        quantity = self._get_or_create_quantity(price)

        if action == settings.BASKET_REMOVE and quantity.count < count:
            raise serializers.ValidationError(
                detail="You can't remove more items than in basket.",
                code="cant_perform_item_remove",
            )

    def add_item(self, order: Order, price: Price, count: int) -> OrderContainer:
        """
        Action for basket, adds item to basket.
        """

        basket = self.basket

        with atomic():
            quantity = self._get_or_create_quantity(price)
            quantity.count = F("count") + count
            quantity.save()

        return basket

    def remove_item(self, order: Order, price: Price, count: int) -> OrderContainer:
        """
        Action for basket, removes item from basket.
        """

        basket = self.basket

        with atomic():
            quantity = self._get_or_create_quantity(price)
            current_count = quantity.count - count

            # this expression has a lazy evaluation
            # at database side
            quantity.count = F("count") - count
            quantity.save()

            # we need to check a value after we will apply
            # `F`-expression
            if current_count == DEFAULT_COUNT:
                quantity.delete()

        return basket

    def clear_all(self):
        """
        Action for basket, removes all items from basket.
        """

        basket = self.basket

        with atomic():
            basket.item_list.set([])
            basket.save()

        return basket

    def set_extra_items(self, extra_items: List):
        """
        Allows to set `extra_items` on Basket.
        """

        basket = self.basket

        with atomic():
            basket.extra_items = extra_items
            basket.save()

        return basket

    def _get_or_create_quantity(self, price: Price) -> Quantity:
        quantity, _ = Quantity.objects.get_or_create(
            basket=self.basket,
            price=price,
            defaults={
                "count": DEFAULT_COUNT,
            },
        )

        return quantity

    @property
    def basket(self) -> Basket:
        order = self._order
