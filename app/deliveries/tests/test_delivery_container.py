from unittest.mock import MagicMock

from deliveries.containers import DeliveryContainer
from subscriptions.choices import Package


#
# PAYC
#
def test_payc_small_load():
    subscription = MagicMock()
    subscription.name = Package.PAYC
    subscription.delivery_free_from = 4900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [0, 1990, 0],
        [1500, 1990, 0],
        [2999, 1990, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_payc_medium_load():
    subscription = MagicMock()
    subscription.name = Package.PAYC
    subscription.delivery_free_from = 4900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [3000, 990, 0],
        [4000, 990, 0],
        [4899, 990, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_payc_free():
    subscription = MagicMock()
    subscription.name = Package.PAYC
    subscription.delivery_free_from = 4900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [4900, 990, 990],
        [5500, 990, 990],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


#
# GOLD
#
def test_gold_small_load():
    subscription = MagicMock()
    subscription.name = Package.GOLD
    subscription.delivery_free_from = 3900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [0, 1498, 0],
        [1250, 1498, 0],
        [2499, 1498, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_gold_medium_load():
    subscription = MagicMock()
    subscription.name = Package.GOLD
    subscription.delivery_free_from = 3900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [2600, 990, 0],
        [3300, 990, 0],
        [3899, 990, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_gold_free():
    subscription = MagicMock()
    subscription.name = Package.GOLD
    subscription.delivery_free_from = 3900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [3900, 990, 990],
        [4500, 990, 990],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


#
# PLATINUM
#
def test_platinum_small_load():
    subscription = MagicMock()
    subscription.name = Package.PLATINUM
    subscription.delivery_free_from = 3900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [0, 1498, 0],
        [1250, 1498, 0],
        [2499, 1498, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_platinum_medium_load():
    subscription = MagicMock()
    subscription.name = Package.PLATINUM
    subscription.delivery_free_from = 3900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [2600, 990, 0],
        [3300, 990, 0],
        [3899, 990, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_platinum_free():
    subscription = MagicMock()
    subscription.name = Package.PLATINUM
    subscription.delivery_free_from = 3900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [3900, 990, 990],
        [4500, 990, 990],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount
