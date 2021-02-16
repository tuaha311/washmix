from django.conf import settings

from core.containers import BaseDynamicAmountContainer
from core.utils import get_dollars
from deliveries.containers.delivery import DeliveryContainer
from deliveries.models import Request
from orders.containers.basket import BasketContainer
from subscriptions.models import Subscription


class RequestContainer(BaseDynamicAmountContainer):
    """
    Wrapper container around pickup and dropoff Delivery
    """

    proxy_to_object = "_request"

    def __init__(
        self,
        subscription: Subscription,
        request: Request,
        basket: BasketContainer,
    ):
        self._subscription = subscription
        self._request = request
        self._basket = basket

    @property
    def amount(self) -> int:
        custom_amount = self.custom_amount
        pickup_container = self.pickup_container
        dropoff_container = self.dropoff_container

        container_list = [pickup_container, dropoff_container]
        amount_list = [item.amount for item in container_list]

        total_amount = sum(amount_list)

        if custom_amount:
            total_amount = custom_amount

        return total_amount

    @property
    def discount(self) -> int:
        custom_amount = self.custom_amount
        pickup_container = self.pickup_container
        dropoff_container = self.dropoff_container

        container_list = [pickup_container, dropoff_container]
        discount_list = [item.discount for item in container_list]

        total_discount = sum(discount_list)

        if custom_amount:
            total_discount = settings.DEFAULT_ZERO_DISCOUNT

        return total_discount

    @property
    def is_free(self) -> bool:
        return self.amount == self.discount

    @property
    def dollar_rush_amount(self) -> float:
        return get_dollars(self, "rush_amount")

    @property
    def pickup_container(self) -> DeliveryContainer:
        subscription = self._subscription
        basket = self._basket
        pickup = self._request.pickup

        pickup_container = DeliveryContainer(subscription, pickup, basket)

        return pickup_container

    @property
    def dropoff_container(self) -> DeliveryContainer:
        subscription = self._subscription
        basket = self._basket
        dropoff = self._request.dropoff

        dropoff_container = DeliveryContainer(subscription, dropoff, basket)

        return dropoff_container
