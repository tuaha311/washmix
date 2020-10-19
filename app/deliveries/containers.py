from django.conf import settings

from core.utils import get_dollars
from deliveries.models import Delivery
from subscriptions.choices import Package
from subscriptions.models import Subscription
from users.models import Client


class DeliveryDiscountService:
    def __init__(self, client: Client, subscription: Subscription, delivery: Delivery):
        self._client = client
        self._subscription = subscription

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
