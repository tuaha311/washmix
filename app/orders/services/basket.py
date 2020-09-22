from orders.models import Basket, Price
from users.models import Client


class BasketService:
    def __init__(self, client: Client):
        self._client = client

    @property
    def basket(self) -> Basket:
        pass

    def add_item(self, price: Price, count: int):
        pass

    def remove_item(self, price: Price, count: int):
        pass

    def clear_all(self):
        pass

    def checkout(self):
        pass
