from orders.models import Quantity
from orders.services.discount import DiscountService


def get_discount_for_quantity(quantity: Quantity):
    basket = quantity.basket
    client = basket.client
    subscription = client.subscription

    service = DiscountService(client, basket)
    discount = service.get_discount_for_service(quantity, subscription)

    return discount
