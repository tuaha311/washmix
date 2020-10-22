from django.conf import settings

from core.containers import BaseAmountContainer
from deliveries.models import Delivery
from orders.containers.basket import BasketContainer
from subscriptions.choices import Package
from subscriptions.models import Subscription


class DeliveryContainer(BaseAmountContainer):
    """
    Reference to Delivery Fees - https://washmix.evrone.app/terms-of-use
    """

    proxy_to_object = "_delivery"
    price_map = {
        Package.PAYC: {
            "price_list": [
                {"min": 0, "max": 2999, "price": 1990,},
                {"min": 3000, "max": 4899, "price": 990,},
            ],
            "discount_from": settings.PAYC_FREE_DELIVERY_FROM,
        },
        Package.GOLD: {
            "price_list": [
                {"min": 0, "max": 2499, "price": 1498,},
                {"min": 2600, "max": 3899, "price": 990,},
            ],
            "discount_from": settings.GOLD_PLATINUM_FREE_DELIVERY_FROM,
        },
        Package.PLATINUM: {
            "price_list": [
                {"min": 0, "max": 2499, "price": 1498,},
                {"min": 2600, "max": 3899, "price": 990,},
            ],
            "discount_from": settings.GOLD_PLATINUM_FREE_DELIVERY_FROM,
        },
    }

    def __init__(
        self, subscription: Subscription, delivery: Delivery, basket: BasketContainer,
    ):
        self._subscription = subscription
        self._delivery = delivery
        self._basket = basket

    @property
    def amount(self) -> int:
        subscription = self._subscription
        basket = self._basket
        price_map = self.price_map[subscription.name]
        price_list = price_map["price_list"]

        for item in price_list:
            min_value = item["min"]
            max_value = item["max"]
            price = item["price"]

            if min_value <= basket.amount <= max_value:
                amount = price

        return amount

    @property
    def is_free(self):
        amount = self.amount
        return amount == settings.FREE_DELIVERY_PRICE

    @property
    def discount(self):
        return settings.FREE_DELIVERY_PRICE
