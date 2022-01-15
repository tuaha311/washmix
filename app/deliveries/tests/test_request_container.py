from unittest.mock import MagicMock

from deliveries.containers.delivery import DeliveryContainer
from subscriptions.choices import Package


#
# PAYC
#
def test_payc_small_load():
    subscription = MagicMock()
    subscription.name = Package.PAYC
    subscription.delivery_free_from = 6900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [0, 995, 0],
        [1500, 995, 0],
        [2999, 995, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_payc_medium_load():
    subscription = MagicMock()
    subscription.name = Package.PAYC
    subscription.delivery_free_from = 6900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [5000, 495, 0],
        [5500, 495, 0],
        [6899, 495, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_payc_free():
    subscription = MagicMock()
    subscription.name = Package.PAYC
    subscription.delivery_free_from = 6900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [6900, 0, 0],
        [7500, 0, 0],
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
    subscription.delivery_free_from = 5900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [0, 745, 0],
        [1250, 745, 0],
        [2499, 745, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_gold_medium_load():
    subscription = MagicMock()
    subscription.name = Package.GOLD
    subscription.delivery_free_from = 5900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [4900, 495, 0],
        [5500, 495, 0],
        [5899, 495, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_gold_free():
    subscription = MagicMock()
    subscription.name = Package.GOLD
    subscription.delivery_free_from = 5900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [5900, 0, 0],
        [6500, 0, 0],
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
    subscription.delivery_free_from = 4900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [0, 745, 0],
        [1250, 745, 0],
        [2499, 745, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_platinum_medium_load():
    subscription = MagicMock()
    subscription.name = Package.PLATINUM
    subscription.delivery_free_from = 4900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [2900, 495, 0],
        [3300, 495, 0],
        [4899, 495, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount


def test_platinum_free():
    subscription = MagicMock()
    subscription.name = Package.PLATINUM
    subscription.delivery_free_from = 4900
    delivery = MagicMock()
    basket = MagicMock()
    amount_list = [
        [4900, 0, 0],
        [5500, 0, 0],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount
