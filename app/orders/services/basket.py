from django.db.transaction import atomic

from orders.models import Basket, Price, Quantity
from users.models import Client


class BasketService:
    def __init__(self, client: Client):
        self._client = client

    @property
    def basket(self) -> Basket:
        basket, _ = Basket.objects.get_or_create(client=self._client, order__isnull=True,)
        return basket

    def validate(self):
        pass

    def get_or_create_quantity(self, price: Price) -> Quantity:
        quantity, _ = Quantity.objects.get_or_create(
            basket=self.basket, price=price, defaults={"count": 0,},
        )
        return quantity

    def add_item(self, price: Price, count: int) -> Basket:
        with atomic():
            quantity = self.get_or_create_quantity(price)

            # TODO использовать F-expression
            quantity.count += count
            quantity.save()

        return self.basket

    def remove_item(self, price: Price, count: int) -> Basket:
        with atomic():
            quantity = self.get_or_create_quantity(price)

            # TODO использовать F-expression
            quantity.count -= count
            quantity.save()

        return self.basket

    def clear_all(self):
        self.basket.item_list.set([])
        self.basket.save()

    def checkout(self):
        pass
