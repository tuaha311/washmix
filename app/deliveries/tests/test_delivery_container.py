from unittest.mock import MagicMock, patch

from deliveries.containers import DeliveryContainer
from subscriptions.choices import Package


#
# PAYC
#
def test_payc_small_load():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.PAYC
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [0, 1990],
        [1500, 1990],
        [2999, 1990],
    ]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result


def test_payc_medium_load():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.PAYC
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [[3000, 990], [4000, 990], [4899, 990]]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result


def test_payc_free():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.PAYC
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [4900, 0],
        [5500, 0],
    ]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result


#
# GOLD
#
def test_gold_small_load():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.GOLD
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [[0, 1498], [1250, 1498], [2499, 1498]]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result


def test_gold_medium_load():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.GOLD
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [[2600, 990], [3300, 990], [3899, 990]]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result


def test_gold_free():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.GOLD
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [3900, 0],
        [4500, 0],
    ]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result


#
# PLATINUM
#
def test_platinum_small_load():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.PLATINUM
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [[0, 1498], [1250, 1498], [2499, 1498]]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result


def test_platinum_medium_load():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.PLATINUM
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [[2600, 990], [3300, 990], [3899, 990]]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result


def test_platinum_free():
    client = MagicMock()
    subscription = MagicMock()
    subscription.name = Package.PLATINUM
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [3900, 0],
        [4500, 0],
    ]

    for amount, result in amount_list:
        basket.amount = amount
        container = DeliveryContainer(client, subscription, delivery, basket)
        assert container.amount == result
