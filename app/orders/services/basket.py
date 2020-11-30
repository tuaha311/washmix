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
            current_count = quantity.count - count

            # this expression has a lazy evaluation
            # at database side
            quantity.count = F("count") - count
            quantity.save()

            # we need to check a value after we will apply
            # `F`-expression
            if current_count == DEFAULT_COUNT:
                quantity.delete()

        return self.get_container()

    def clear_all(self):
        """
        Action for basket, removes all items from basket.
        """

        basket = self.basket

        with atomic():
            basket.item_list.set([])
            basket.save()

        return self.get_container()

    def get_container(self) -> OrderContainer:
        order_service = self.get_order_service()
        order_container = order_service.get_container()

        return order_container

    def get_order_service(self) -> OrderService:
        client = self._client
        basket = self.basket

        # we are looking for last order, that was created for basket
        # and wasn't paid
        order, _ = Order.objects.get_or_create(client=client, basket=basket)
        order_service = OrderService(client, order)

        return order_service

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
        client = self._client

        # we are looking for last basket, that wasn't paid
        basket, _ = Basket.objects.get_or_create(
            client=client,
            invoice__transaction_list__isnull=True,
            defaults={
                "invoice": None,
            },
        )

        return basket
