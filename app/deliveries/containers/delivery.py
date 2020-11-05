from typing import Tuple

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
                # 0 - 2999 price 19.90$
                {
                    "min": 0,
                    "max": 2999,
                    "price": 995,
                },
                # 3000 - 4899 price 9.90$
                {
                    "min": 3000,
                    "max": 4899,
                    "price": 495,
                },
                # 4900 - infinity price 9.90$
                {
                    "min": 4900,
                    "max": float("inf"),
                    "price": 495,
                },
            ],
        },
        Package.GOLD: {
            "price_list": [
                # 0 - 2499 price 14.98$
                {
                    "min": 0,
                    "max": 2499,
                    "price": 749,
                },
                # 2500 - 3899 price 9.90$
                {
                    "min": 2500,
                    "max": 3899,
                    "price": 495,
                },
                # 3900 - infinity price 9.90$
                {
                    "min": 3900,
                    "max": float("inf"),
                    "price": 495,
                },
            ],
        },
        Package.PLATINUM: {
            "price_list": [
                # 0 - 2499 price 14.98$
                {
                    "min": 0,
                    "max": 2499,
                    "price": 749,
                },
                # 2500 - 3899 price 9.90$
                {
                    "min": 2500,
                    "max": 3899,
                    "price": 495,
                },
                # 3900 - infinity price 9.90$
                {
                    "min": 3900,
                    "max": float("inf"),
                    "price": 495,
                },
            ],
        },
    }

    def __init__(
        self,
        subscription: Subscription,
        delivery: Delivery,
        basket: BasketContainer,
    ):
        self._subscription = subscription
        self._delivery = delivery
        self._basket = basket

    @property
    def amount(self) -> int:
        amount, _ = self._get_amount_discount()
        return amount

    @property
    def discount(self) -> int:
        _, discount = self._get_amount_discount()
        return discount

    @property
    def is_free(self) -> bool:
        return self.amount == self.discount

    def _get_amount_discount(self) -> Tuple[int, int]:
        subscription = self._subscription
        basket = self._basket
        price_map = self.price_map[subscription.name]
        price_list = price_map["price_list"]
        discount_from = subscription.delivery_free_from
        discount = settings.DEFAULT_ZERO_DISCOUNT

        for item in price_list:
            min_value = item["min"]
            max_value = item["max"]
            price = item["price"]

            if min_value <= basket.amount <= max_value:
                amount = price

        if basket.amount >= discount_from:
            discount = amount

        return amount, discount
