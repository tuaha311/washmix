from core.utils import get_dollars
from orders.models import Basket
from subscriptions.models import Subscription
from users.models import Client


class BasketContainer:
    def __init__(self, client: Client, subscription: Subscription, basket: Basket):
        self._client = client
        self._subscription = subscription
        self._basket = basket

    @property
    def amount(self) -> int:
        return self._calculate_sum("amount")

    @property
    def dollar_amount(self) -> float:
        return get_dollars(self, "amount")

    @property
    def discount(self) -> int:
        return self._calculate_sum("discount")

    @property
    def dollar_discount(self) -> float:
        return get_dollars(self, "discount")

    @property
    def amount_with_discount(self) -> int:
        return self._calculate_sum("amount_with_discount")

    @property
    def dollar_amount_with_discount(self) -> float:
        return get_dollars(self, "amount_with_discount")

    def _calculate_sum(self, item_attribute_name: str) -> int:
        basket = self._basket
        quantity_list = basket.quantity_list.all()
        amount = [getattr(item, item_attribute_name) for item in quantity_list]

        return sum(amount)
