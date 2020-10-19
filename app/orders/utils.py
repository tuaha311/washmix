from deliveries.models import Delivery
from deliveries.services.discount import DeliveryDiscountService
from orders.models import Quantity
from orders.services.discount import QuantityDiscountService


def get_discount_for_quantity(quantity: Quantity):
    basket = quantity.basket
    client = basket.client
    subscription = client.subscription

    service = QuantityDiscountService(client, subscription)
    discount = service.get_discount(quantity)

    return discount


def get_discount_for_delivery(delivery: Delivery):
    client = delivery.client
    subscription = client.subscription

    service = DeliveryDiscountService(client, subscription)
    discount = service.get_discount(delivery)

    return discount
