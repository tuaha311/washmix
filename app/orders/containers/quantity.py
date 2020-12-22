from typing import Dict

from django.conf import settings

from core.containers import BaseAmountContainer
from orders.models import Quantity, Service
from subscriptions.models import Subscription


class QuantityContainer(BaseAmountContainer):
    proxy_to_object = "_quantity"
    service_list = [
        {
            "attribute_name": "dry_clean",
            "title": "Dry Cleaning",
        },
        {
            "attribute_name": "laundry",
            "title": "Laundry",
        },
        {
            "attribute_name": "alterations",
            "title": "Alterations & Repair",
        },
        {
            "attribute_name": "wash_fold",
            "title": "Wash & Folds",
        },
    ]

    def __init__(self, subscription: Subscription, quantity: Quantity):
        self._subscription = subscription
        self._quantity = quantity

    @property
    def amount(self) -> int:
        quantity = self._quantity
        return quantity.price.amount * quantity.count

    @property
    def discount(self) -> int:
        return self._get_discount()

    def _get_discount(self) -> int:
        """
        Returns discount amount for Service based on Subscription discount for this category.
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
