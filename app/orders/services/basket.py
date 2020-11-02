from django.conf import settings
from django.db.models import F
from django.db.transaction import atomic

from rest_framework import serializers

from orders.containers.order import OrderContainer
from orders.models import Basket, Order, Price, Quantity
from orders.services.order import OrderService
from users.models import Client

DEFAULT_COUNT = 0


class BasketService:
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

    def validate(self, price: Price, count: int, action: str):
        quantity = self._get_or_create_quantity(price)

        if action == settings.BASKET_REMOVE and quantity.count < count:
            raise serializers.ValidationError(
                detail="You can't remove more items than in basket.",
                code="cant_perform_item_remove",
            )

    def add_item(self, price: Price, count: int) -> OrderContainer:
        """
        Action for basket, adds item to basket.
        """

        with atomic():
            quantity = self._get_or_create_quantity(price)
            quantity.count = F("count") + count
            quantity.save()

        return self.get_container()

    def remove_item(self, price: Price, count: int) -> OrderContainer:
        """
        Action for basket, removes item from basket.
        """

        with atomic():
            quantity = self._get_or_create_quantity(price)
            quantity.count = F("count") - count
            quantity.save()

            if quantity.count == DEFAULT_COUNT:
                quantity.delete()

        return self.get_container()

    def clear_all(self):
        """
        Action for basket, removes all items from basket.
        """

        self.basket.item_list.set([])
        self.basket.save()

    def _get_or_create_quantity(self, price: Price) -> Quantity:
        quantity, _ = Quantity.objects.get_or_create(
            basket=self.basket, price=price, defaults={"count": DEFAULT_COUNT,},
        )

        return quantity

    @property
    def basket(self) -> Basket:
        client = self._client
        basket, _ = Basket.objects.get_or_create(client=client, invoice__isnull=True)
        return basket

    def get_container(self) -> OrderContainer:
        client = self._client
        basket = self.basket

        order, _ = Order.objects.get_or_create(client=client, basket=basket)

        order_service = OrderService(client, order)
        order_container = order_service.get_container()

        return order_container
