from typing import Dict, List, Tuple

from django.conf import settings

from core.containers import BaseAmountContainer
from core.utils import get_dollars
from deliveries.models import Delivery
from orders.containers.basket import BasketContainer
from subscriptions.choices import Package
from subscriptions.models import Subscription


class DeliveryContainer(BaseAmountContainer):
    """
    Reference to Delivery Fees - https://washmix.evrone.app/terms-of-use

    DeliveryContainer implements pricing logic of delivery.
    Pricing on delivery depends on:
        - Subscription
        - Basket amount
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
                # 0 - 24.99$ price 14.98$
                # if higher than 24.99 - free delivery
                {
                    "min": 0,
                    "max": 2499,
                    "price": 749,
                },
                # 25.00 - 38.99$ price 9.90$
                # if higher than 38.99$ - free delivery
                {
                    "min": 2500,
                    "max": 3899,
                    "price": 495,
                },
                # 3900 - infinity price 9.90$
                # if higher than 39.00$ - free delivery
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

    @property
    def rush_amount(self) -> int:
        amount = 0
        is_rush = self.is_rush

        if is_rush:
            amount += settings.RUSH_DELIVERY_PRICE

        return amount

    @property
    def dollar_rush_amount(self) -> float:
        return get_dollars(self, "rush_amount")

    def _get_amount_discount(self) -> Tuple[int, int]:
        subscription = self._subscription
        basket = self._basket
        price_map: Dict = self.price_map[subscription.name]
        price_list: List[Dict] = price_map["price_list"]
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
