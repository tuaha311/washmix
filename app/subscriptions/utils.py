from typing import Optional

from django.conf import settings

from subscriptions.models import Subscription


def is_advantage_program(name: str) -> bool:
    """
    Checks client's subscription includes in Advantage Program
    """

    in_advantage_prorgam = name in [settings.GOLD, settings.PLATINUM]

    return in_advantage_prorgam


def get_direction_of_subscription(
    old_subscription: Optional[Subscription],
    future_subscription: Subscription,
    is_replenished: bool = False,
):
    """
    Get direction of upgrade or downgrade subscriptions by client.
    """

    if is_replenished:
        return settings.SUBSCRIPTION_REPLENISHED

    if not old_subscription:
        return settings.SUBSCRIPTION_UPGRADE

    old_subscription_name = old_subscription.name
    old_subscription_index = settings.PACKAGE_NAME_ORDERING.index(old_subscription_name)
    future_subscription_name = future_subscription.name
    future_subscription_index = settings.PACKAGE_NAME_ORDERING.index(future_subscription_name)

    if old_subscription_index == future_subscription_index:
        return settings.SUBSCRIPTION_UPGRADE

    elif old_subscription_index > future_subscription_index:
        return settings.SUBSCRIPTION_DOWNGRADE

    else:
        return settings.SUBSCRIPTION_UPGRADE
