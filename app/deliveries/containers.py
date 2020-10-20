from django.conf import settings

from core.containers import BaseAmountContainer
from deliveries.models import Delivery
from orders.containers.basket import BasketContainer
from subscriptions.choices import Package
from subscriptions.models import Subscription
from users.models import Client

PAYC_FREE_DELIVERY_THRESHOLD = 4900
GOLD_PLATINUM_FREE_DELIVERY_THRESHOLD = 3900


class DeliveryContainer(BaseAmountContainer):
    """
    Reference to Delivery Fees - https://washmix.evrone.app/terms-of-use
    """

    proxy_to_object = "_delivery"
    price_map = {
        Package.PAYC: {
            "free_threshold": PAYC_FREE_DELIVERY_THRESHOLD,
            "price_list": [
                {"min": 0, "max": 2999, "price": 1990,},
                {"min": 3000, "max": 4899, "price": 990,},
            ],
        },
        Package.GOLD: {
            "free_threshold": GOLD_PLATINUM_FREE_DELIVERY_THRESHOLD,
            "price_list": [
                {"min": 0, "max": 2499, "price": 1498,},
                {"min": 2600, "max": 3899, "price": 990,},
            ],
        },
        Package.PLATINUM: {
            "free_threshold": GOLD_PLATINUM_FREE_DELIVERY_THRESHOLD,
            "price_list": [
                {"min": 0, "max": 2499, "price": 1498,},
                {"min": 2600, "max": 3899, "price": 990,},
            ],
        },
    }

    def __init__(
        self,
        client: Client,
        subscription: Subscription,
        delivery: Delivery,
        basket: BasketContainer,
    ):
        self._client = client
        self._subscription = subscription
        self._delivery = delivery
        self._basket = basket

    @property
    def amount(self) -> int:
        subscription = self._subscription
        basket = self._basket
        price_map = self.price_map[subscription.name]
        free_threshold = price_map["free_threshold"]
        price_list = price_map["price_list"]

        if basket.amount >= free_threshold:
            return settings.FREE_DELIVERY_PRICE

        for item in price_list:
            min_value = item["min"]
            max_value = item["max"]
            price = item["price"]

            if min_value <= basket.amount <= max_value:
                return price

    @property
    def discount(self) -> int:
        pass

    @property
    def amount_with_discount(self) -> int:
        amount = self.amount
        discount = self.discount

        return amount - discount
