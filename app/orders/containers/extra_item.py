from django.conf import settings

from core.containers import BaseDynamicAmountContainer


class ExtraItemContainer(BaseDynamicAmountContainer):
    proxy_to_object = "_extra_item"
    subscription_attribute_name = "dry_clean"

    def __init__(self, subscription, extra_item):
        self._subscription = subscription
        self._extra_item = extra_item

    @property
    def discount(self) -> float:
        subscription = self._subscription
        subscription_attribute_name = self.subscription_attribute_name
        amount = self.amount

        try:
            subscription_discount_for_service = getattr(subscription, subscription_attribute_name)
            discount = amount * subscription_discount_for_service / settings.PERCENTAGE
        except (KeyError, AttributeError):
            discount = settings.DEFAULT_ZERO_DISCOUNT
        finally:
            return discount

    @property
    def amount(self):
        extra_item = self._extra_item

        return extra_item["amount"]

    @property
    def title(self):
        extra_item = self._extra_item

        return extra_item["title"]

    @property
    def instructions(self):
        extra_item = self._extra_item

        return extra_item["instructions"]
