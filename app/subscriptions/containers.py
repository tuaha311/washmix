from django.conf import settings

from core.containers import BaseAmountContainer
from subscriptions.models import Subscription


class SubscriptionContainer(BaseAmountContainer):
    proxy_to_object = "_subscription"

    def __init__(self, subscription: Subscription):
        self._subscription = subscription

    @property
    def amount(self) -> int:
        return self._subscription.price

    @property
    def discount(self) -> int:
        return settings.DEFAULT_ZERO_DISCOUNT
