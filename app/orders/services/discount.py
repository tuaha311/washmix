from typing import Dict

from django.conf import settings

from orders.models import Basket, Quantity, Service
from subscriptions.models import Subscription
from users.models import Client


class DiscountService:
    service_list = [
        {"attribute_name": "dry_clean", "title": "Dry Cleaning",},
        {"attribute_name": "laundry", "title": "Laundry",},
        {"attribute_name": "alterations", "title": "Alterations & Repair",},
        {"attribute_name": "wash_fold", "title": "Wash & Folds",},
    ]

    def __init__(self, client: Client, basket: Basket):
        self._client = client
        self._basket = basket

    def get_discount_for_service(self, quantity: Quantity, subscription: Subscription):
        service = quantity.price.service
        service_map = self.service_map

        try:
            attribute_name = service_map[service]
            subscription_discount_for_service = getattr(subscription, attribute_name)
            discount = quantity.amount * subscription_discount_for_service / settings.PERCENTAGE
        except (KeyError, AttributeError):
            discount = settings.DEFAULT_DISCOUNT
        finally:
            return discount

    @property
    def service_map(self) -> Dict[Service, str]:
        result = {}

        for item in self.service_list:
            title = item["title"]
            attribute_name = item["attribute_name"]

            service = Service.objects.get(title=title)
            result[service] = attribute_name

        return result
