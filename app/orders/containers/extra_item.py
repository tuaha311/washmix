from core.containers import BaseDynamicAmountContainer
from orders.helpers import calculate_discount


class ExtraItemContainer(BaseDynamicAmountContainer):
    proxy_to_object = "_extra_item"
    subscription_attribute_name = "dry_clean"

    def __init__(self, subscription, extra_item):
        self._subscription = subscription
        self._extra_item = extra_item

    @property
    def discount(self) -> float:
        subscription = self._subscription
        attribute_name = self.subscription_attribute_name
        amount = self.amount

        discount = calculate_discount(amount, subscription, attribute_name)

        return discount

    @property
    def amount(self):
        extra_item = self._extra_item

        return extra_item["amount"]

    @property
    def title(self):
        extra_item = self._extra_item

        return extra_item["title"]

    @property
    def instructions(self):
        extra_item = self._extra_item

        return extra_item["instructions"]
