from typing import Dict, List, Tuple

from django.conf import settings

from core.containers import BaseDynamicAmountContainer
from deliveries.models import Delivery
from orders.containers.basket import BasketContainer
from subscriptions.choices import Package
from subscriptions.models import Subscription


class DeliveryContainer(BaseDynamicAmountContainer):
    """
    Reference to Delivery Fees - https://washmix.com/terms-of-use

    DeliveryContainer implements pricing logic of delivery.
    Pricing on delivery depends on:
        - Subscription
        - Basket amount
    """

    proxy_to_object = "_delivery"
    price_map = {
        Package.PAYC: {
            "price_list": [
                # $1-$48 [$19.90 Delivery FEE]
                #
                # $49-$69 [$9.90 Delivery FEE]
                #
                # FREE Delivery with $69
                {
                    "min": 0,
                    "max": 4899,
                    "price": 995,
                },
                {
                    "min": 4900,
                    "max": 6899,
                    "price": 495,
                },
                {
                    "min": 6900,
                    "max": float("inf"),
                    "price": 0,
                },
            ],
        },
        Package.GOLD: {
            "price_list": [
                # $1-$48 [$14.90 Delivery FEE]
                #
                # $49-$59 [$9.90 Delivery FEE]
                #
                # FREE Delivery with $59
                {
                    "min": 0,
                    "max": 4899,
                    "price": 745,
                },
                {
                    "min": 4900,
                    "max": 5899,
                    "price": 495,
                },
                {
                    "min": 5900,
                    "max": float("inf"),
                    "price": 0,
                },
            ],
        },
        Package.PLATINUM: {
            "price_list": [
                # $1-$28 [$14.90 Delivery FEE]
                #
                # $29-$49 [$9.90 Delivery FEE]
                #
                # FREE Delivery with $49
                {
                    "min": 0,
                    "max": 2899,
                    "price": 745,
                },
                {
                    "min": 2900,
                    "max": 4899,
                    "price": 495,
                },
                {
                    "min": 4900,
                    "max": float("inf"),
                    "price": 0,
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
