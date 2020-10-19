from typing import Dict

from django.conf import settings

from core.utils import get_dollars
from orders.models import Quantity, Service
from subscriptions.models import Subscription


class QuantityContainer:
    service_list = [
        {"attribute_name": "dry_clean", "title": "Dry Cleaning",},
        {"attribute_name": "laundry", "title": "Laundry",},
        {"attribute_name": "alterations", "title": "Alterations & Repair",},
        {"attribute_name": "wash_fold", "title": "Wash & Folds",},
    ]

    def __init__(self, subscription: Subscription, quantity: Quantity):
        self._subscription = subscription
        self._quantity = quantity

    def __getattr__(self, item):
        """
        This method invoked only when we can't find attribute name in itself.
        Method works as a fallback.
        """

        quantity = self._quantity
        return getattr(quantity, item)

    @property
    def amount(self) -> int:
        quantity = self._quantity
        return quantity.price.amount * quantity.count

    @property
    def dollar_amount(self) -> float:
        return get_dollars(self, "amount")

    @property
    def discount(self) -> int:
        return self._get_discount()

    @property
    def dollar_discount(self) -> float:
        return get_dollars(self, "discount")

    @property
    def amount_with_discount(self) -> int:
        amount = self.amount
        discount = self.discount

        return amount - discount

    @property
    def dollar_amount_with_discount(self) -> float:
        return get_dollars(self, "amount_with_discount")

    def _get_discount(self) -> int:
        """
        Returns discount amount for Service based on Service category.
        """

        quantity = self._quantity
        service = quantity.price.service
        service_map = self._service_map
        subscription = self._subscription

        try:
            attribute_name = service_map[service]
            subscription_discount_for_service = getattr(subscription, attribute_name)
            discount = self.amount * subscription_discount_for_service / settings.PERCENTAGE
        except (KeyError, AttributeError):
            discount = settings.DEFAULT_ZERO_DISCOUNT
        finally:
            return discount

    @property
    def _service_map(self) -> Dict[Service, str]:
        """
        Using this you can retrieve discount's attribute name of `Subscription` model.

        Subscription has following discount's attributes,
        that holds an discount of service category:
            - dry_clean
            - laundry
            - alterations
            - wash_fold
        """

        result = {}

        for item in self.service_list:
            title = item["title"]
            attribute_name = item["attribute_name"]

            service = Service.objects.get(title=title)
            result[service] = attribute_name

        return result
