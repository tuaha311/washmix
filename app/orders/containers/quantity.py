from core.containers import BaseDynamicAmountContainer
from orders.helpers import calculate_discount, get_service_map
from orders.models import Quantity
from subscriptions.models import Subscription


class QuantityContainer(BaseDynamicAmountContainer):
    proxy_to_object = "_quantity"
    default_attribute_name = "dry_clean"

    def __init__(self, subscription: Subscription, quantity: Quantity):
        self._subscription = subscription
        self._quantity = quantity

    @property
    def amount(self) -> int:
        quantity = self._quantity
        return quantity.price.amount * quantity.count

    @property
    def discount(self) -> int:
        return self._get_discount()

    def _get_discount(self) -> int:
        """
        Returns discount amount for Service based on Subscription discount attribute
        for this category.
        """

        quantity = self._quantity
        amount = self.amount
        service = quantity.price.service
        subscription = self._subscription

        service_map = get_service_map()
        attribute_name = service_map.get(service, self.default_attribute_name)

        discount = calculate_discount(amount, subscription, attribute_name)

        return discount
