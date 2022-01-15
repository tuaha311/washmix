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
        [3000, 495, 0],
        [4000, 495, 0],
        [4899, 495, 0],
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
        [4900, 495, 495],
        [5500, 495, 495],
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
        [0, 749, 0],
        [1250, 749, 0],
        [2499, 749, 0],
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
        [2600, 495, 0],
        [3300, 495, 0],
        [3899, 495, 0],
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
        [3900, 495, 495],
        [4500, 495, 495],
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
        [0, 749, 0],
        [1250, 749, 0],
        [2499, 749, 0],
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
        [2600, 495, 0],
        [3300, 495, 0],
        [3899, 495, 0],
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
        [3900, 495, 495],
        [4500, 495, 495],
    ]

    for basket_amount, delivery_amount, delivery_discount in amount_list:
        basket.amount = basket_amount
        container = DeliveryContainer(subscription, delivery, basket)
        assert container.amount == delivery_amount
        assert container.discount == delivery_discount
