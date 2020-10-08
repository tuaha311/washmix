from typing import Dict, List

from django.conf import settings

from core.utils import get_dollars
from orders.models import Basket, Service
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

    @property
    def service_map(self) -> Dict[Service, str]:
        result = {}

        for item in self.service_list:
            title = item["title"]
            attribute_name = item["attribute_name"]

            service = Service.objects.get(title=title)
            result[service] = attribute_name

        return result

    @property
    def discounts(self) -> List[Dict]:
        subscription = self._client.subscription

        if not subscription:
            return []

        result = []
        service_map = self.service_map

        for quantity in self._basket.quantity_list.all():
            service = quantity.price.service

            try:
                attribute_name = service_map[service]
            except KeyError:
                continue

            subscription_discount_for_service = getattr(subscription, attribute_name)
            discount = quantity.amount * subscription_discount_for_service

            result.append(
                {
                    "quantity": quantity,
                    "discount": discount,
                    "dollar_discount": discount / settings.CENTS_IN_DOLLAR,
                }
            )

        return result
