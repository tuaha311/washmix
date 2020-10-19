from deliveries.models import Delivery
from orders.models import Quantity
from orders.services.discount import DiscountService


def get_discount_for_quantity(quantity: Quantity):
    basket = quantity.basket
    client = basket.client
    subscription = client.subscription

    service = DiscountService(client)
    discount = service.get_discount_for_service(quantity, subscription)

    return discount


def get_discount_for_delivery(delivery: Delivery):
    pass
