from core.utils import get_dollars
from orders.containers.quantity import QuantityContainer
from orders.models import Basket
from subscriptions.models import Subscription


class BasketContainer:
    def __init__(self, subscription: Subscription, basket: Basket):
        self._subscription = subscription
        self._basket = basket

    def __getattr__(self, item):
        """
        This method invoked only when we can't find attribute name in itself.
        Method works as a fallback.
        """

        basket = self._basket
        return getattr(basket, item)

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
        subscription = self._subscription

        quantity_list = basket.quantity_list.all()
        quantity_container_list = [QuantityContainer(subscription, item) for item in quantity_list]

        amount = [getattr(item, item_attribute_name) for item in quantity_container_list]

        return sum(amount)
