from typing import List, Optional

from django.conf import settings
from django.db.models import F
from django.db.transaction import atomic

from rest_framework import serializers

from billing.models import Invoice
from billing.services.invoice import InvoiceService
from core.interfaces import PaymentInterfaceService
from deliveries.models import Request
from orders.containers.basket import BasketContainer
from orders.models import Basket, Order, Price, Quantity
from subscriptions.models import Subscription
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

    Order of methods by importance:
        - refresh_amount_with_discount
        - charge
    """

    def __init__(self, client: Client):
        self._client = client

    def refresh_amount_with_discount(
        self,
        order: Order,
        basket: Optional[Basket],
        request: Optional[Request],
        subscription: Optional[Subscription],
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
        basket_container = BasketContainer(subscription, basket)  # type: ignore

        basket = invoice_service.update_amount_discount(
            entity=basket,
            amount=basket_container.amount,
            discount=basket_container.discount,
        )

        return basket.amount_with_discount

    def charge(
        self,
        request: Optional[Request],
        basket: Optional[Basket],
        subscription: Optional[Subscription],
        invoice: Invoice,
        **kwargs,
    ):
        pass

    def checkout(self, **kwargs):
        """
        Dummy implementation of interface.
        """
        pass

    def validate(self, basket: Basket, price: Price, count: int, action: str):
        """
        Makes all validation related stuff.
        """

        quantity = self._get_or_create_quantity(basket, price)

        if action == settings.BASKET_REMOVE and quantity.count < count:
            raise serializers.ValidationError(
                detail="You can't remove more items than in basket.",
                code="cant_perform_item_remove",
            )

    def add_item(self, basket: Basket, price: Price, count: int) -> Basket:
        """
        Action for basket, adds item to basket.
        """

        with atomic():
            quantity = self._get_or_create_quantity(basket, price)
            quantity.count = F("count") + count
            quantity.save()

        return basket

    def remove_item(self, basket: Basket, price: Price, count: int) -> Basket:
        """
        Action for basket, removes item from basket.
        """

        with atomic():
            quantity = self._get_or_create_quantity(basket, price)
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

    def clear_all(self, basket: Basket):
        """
        Action for basket, removes all items from basket.
        """

        with atomic():
            basket.item_list.set([])
            basket.save()

        return basket

    def set_extra_items(self, basket: Basket, extra_items: List):
        """
        Allows to set `extra_items` on Basket.
        """

        with atomic():
            basket.extra_items = extra_items
            basket.save()

        return basket

    def _get_or_create_quantity(self, basket: Basket, price: Price) -> Quantity:
        quantity, _ = Quantity.objects.get_or_create(
            basket=basket,
            price=price,
            defaults={
                "count": DEFAULT_COUNT,
            },
        )

        return quantity
