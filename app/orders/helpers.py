from django.conf import settings

from subscriptions.models import Subscription


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
