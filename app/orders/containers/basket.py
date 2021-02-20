from core.containers import BaseDynamicAmountContainer
from orders.containers.extra_item import ExtraItemContainer
from orders.containers.quantity import QuantityContainer
from orders.models import Basket
from subscriptions.models import Subscription


class BasketContainer(BaseDynamicAmountContainer):
    """
    BasketContainer implements pricing logic of basket.

    Pricing depends on:
        - Subscription
        - Basket amount
    """

    proxy_to_object = "_basket"

    def __init__(self, subscription: Subscription, basket: Basket):
        self._subscription = subscription
        self._basket = basket

    @property
    def amount(self) -> int:
        # first of all, we are aggregating default item prices
        items_amount = self._calculate_sum("amount")

        # then we are adding to them extra items amount
        extra_items = self.extra_items
        extra_items_amount = sum([item.amount for item in extra_items])

        # let's calculate total
        total = items_amount + extra_items_amount

        return total

    @property
    def discount(self) -> int:
        items_discount = self._calculate_sum("discount")

        # then we are adding extra items discount
        extra_items = self.extra_items
        extra_items_discount = sum([item.discount for item in extra_items])

        # let's calculate total
        total = items_discount + extra_items_discount

        return total

    @property
    def quantity_container_list(self):
        basket = self._basket
        subscription = self._subscription

        quantity_list = basket.quantity_list.all()
        quantity_container_list = [QuantityContainer(subscription, item) for item in quantity_list]

        return quantity_container_list

    @property
    def extra_items(self):
        basket = self._basket
        extra_items = basket.extra_items
        subscription = self._subscription

        extra_items_container = [ExtraItemContainer(subscription, item) for item in extra_items]

        return extra_items_container

    def _calculate_sum(self, item_attribute_name: str) -> int:
        quantity_container_list = self.quantity_container_list

        amount = [getattr(item, item_attribute_name) for item in quantity_container_list]

        return sum(amount)
