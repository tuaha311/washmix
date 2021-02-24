from unittest.mock import MagicMock

from django.conf import settings

from subscriptions.utils import get_direction_of_subscription


def test_subscription_is_none():
    old_subscription = None
    future_subscription = MagicMock()
    future_subscription.name = settings.GOLD

    result = get_direction_of_subscription(old_subscription, future_subscription)

    assert result == settings.SUBSCRIPTION_UPGRADE


def test_subscription_is_same():
    old_subscription = MagicMock()
    old_subscription.name = settings.GOLD
    future_subscription = MagicMock()
    future_subscription.name = settings.GOLD

    result = get_direction_of_subscription(old_subscription, future_subscription)

    assert result == settings.SUBSCRIPTION_UPGRADE


def test_subscription_is_upgrading():
    old_subscription = MagicMock()
    old_subscription.name = settings.PAYC
    future_subscription = MagicMock()
    future_subscription.name = settings.PLATINUM

    result = get_direction_of_subscription(old_subscription, future_subscription)

    assert result == settings.SUBSCRIPTION_UPGRADE


def test_subscription_is_downgrading():
    old_subscription = MagicMock()
    old_subscription.name = settings.PLATINUM
    future_subscription = MagicMock()
    future_subscription.name = settings.PAYC

    result = get_direction_of_subscription(old_subscription, future_subscription)

    assert result == settings.SUBSCRIPTION_DOWNGRADE


def test_subscription_is_replenished():
    old_subscription = MagicMock()
    old_subscription.name = settings.PLATINUM
    future_subscription = MagicMock()
    future_subscription.name = settings.PLATINUM
    is_replenish = True

    result = get_direction_of_subscription(old_subscription, future_subscription, is_replenish)

    assert result == settings.SUBSCRIPTION_REPLENISHED
