from functools import lru_cache

from django.conf import settings

from orders.models import Service
from subscriptions.models import Subscription

# this dict maps Service.title to Subscription corresponding attribute name
TITLE_TO_ATTRIBUTE_MAP = {
    "Dry Cleaning": "dry_clean",
    "Laundry": "laundry",
    "Alterations & Repair": "alterations",
    "Wash & Folds": "wash_fold",
}
SERVICE_TITLES = list(TITLE_TO_ATTRIBUTE_MAP.keys())


@lru_cache(maxsize=32)
def get_service_map():
    """
    Using this you can retrieve discount's attribute name of `Subscription` model.

    Subscription has following discount's attributes,
    that holds an discount of service category:
        - dry_clean
        - laundry
        - alterations
        - wash_fold
    """

    service_map = {}
    service_list = Service.objects.filter(title__in=SERVICE_TITLES)

    for service in service_list:
        service_title = service.title
        attribute_name = TITLE_TO_ATTRIBUTE_MAP[service_title]

        service_map[service] = attribute_name

    return service_map


def calculate_discount(amount: int, subscription: Subscription, attribute_name: str):
    """
    Function that calculates discount for Subscription by `attribute_name`.
    By default we have 0 discount.
    """

    discount = settings.DEFAULT_ZERO_DISCOUNT

    try:
        subscription_discount_for_service = getattr(subscription, attribute_name)
        discount = amount * subscription_discount_for_service / settings.PERCENTAGE
    except AttributeError:
        pass
    finally:
        return discount
