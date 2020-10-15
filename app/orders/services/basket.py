from django.conf import settings
from django.db.models import F
from django.db.transaction import atomic

from rest_framework import serializers

from orders.models import Basket, Price, Quantity
from orders.services.discount import DiscountService
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
        self._discount_service = DiscountService(client)

    def validate(self, price: Price, count: int, action: str):
        quantity = self._get_or_create_quantity(price)

        if action == settings.BASKET_REMOVE and quantity.count < count:
            raise serializers.ValidationError(
                detail="You can't remove more items than in basket.",
                code="cant_perform_item_remove",
            )

    def add_item(self, price: Price, count: int) -> Basket:
        """
        Adds item to basket.
        """

        with atomic():
            quantity = self._get_or_create_quantity(price)

            quantity.count = F("count") + count
            quantity.save()

        return self.basket

    def remove_item(self, price: Price, count: int) -> Basket:
        """
        Removes item to basket.
        """

        with atomic():
            quantity = self._get_or_create_quantity(price)

            quantity.count = F("count") - count
            quantity.save()

            if quantity.count == DEFAULT_COUNT:
                quantity.delete()

        return self.basket

    def clear_all(self):
        """
        Clears basket. Removes all items from basket.
        """

        self.basket.item_list.set([])
        self.basket.save()

    @property
    def basket(self) -> Basket:
        basket, _ = Basket.objects.get_or_create(client=self._client, order__isnull=True,)
        return basket

    def _get_or_create_quantity(self, price: Price) -> Quantity:
        quantity, _ = Quantity.objects.get_or_create(
            basket=self.basket, price=price, defaults={"count": DEFAULT_COUNT,},
        )
        return quantity
