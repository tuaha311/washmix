from django.conf import settings

from core.utils import get_dollars
from deliveries.models import Delivery
from orders.models import Basket
from subscriptions.choices import Package
from subscriptions.models import Subscription
from users.models import Client

PAYC_FREE_DELIVERY_THRESHOLD = 4900
GOLD_PLATINUM_FREE_DELIVERY_THRESHOLD = 3900


class DeliveryContainer:
    """
    Reference to Delivery Fees - https://washmix.evrone.app/terms-of-use
    """

    price_map = {
        (Package.PAYC,): {
            "free_threshold": PAYC_FREE_DELIVERY_THRESHOLD,
            "price_list": [
                {"min": 0, "max": 3000, "price": 1990,},
                {"min": 3100, "max": 4800, "price": 990,},
            ],
        },
        (Package.GOLD, Package.PLATINUM,): {
            "free_threshold": GOLD_PLATINUM_FREE_DELIVERY_THRESHOLD,
            "price_list": [
                {"min": 0, "max": 2500, "price": 1498,},
                {"min": 2600, "max": 3800, "price": 990,},
            ],
        },
    }

    def __init__(
        self, client: Client, subscription: Subscription, delivery: Delivery, basket: Basket
    ):
        self._client = client
        self._subscription = subscription
        self._delivery = delivery
        self._basket = basket

    def __getattr__(self, item):
        """
        This method invoked only when we can't find attribute name in itself.
        Method works as a fallback.
        """

        delivery = self._delivery
        return getattr(delivery, item)

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

    def get_discount(self):
        subscription = self._subscription

        if not subscription or subscription.name == Package.PAYC:
            return settings.DEFAULT_ZERO_DISCOUNT

        return settings.DELIVERY_PRICE
