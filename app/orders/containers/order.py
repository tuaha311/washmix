from django.conf import settings

from billing.services.coupon import CouponService
from core.containers import BaseAmountContainer
from core.utils import get_dollars
from orders.containers.basket import BasketContainer
from orders.models import Order


class OrderContainer(BaseAmountContainer):
    proxy_to_object = "_order"

    def __init__(self, order: Order):
        self._order = order

    @property
    def basket(self):
        order = self._order
        client = order.client
        subscription = client.subscription
        basket = order.basket

        container = BasketContainer(subscription, basket)

        return container

    @property
    def amount(self) -> int:
        order = self._order
        invoice_list = order.invoice_list.all()

        amount = sum(item.amount for item in invoice_list)

        return amount

    @property
    def discount(self) -> float:
        order = self._order
        amount = self.amount
        coupon = order.coupon
        coupon_service = CouponService(amount, coupon)

        return coupon_service.apply_coupon()

    @property
    def credit_back(self) -> int:
        amount_with_discount = self.amount_with_discount

        return amount_with_discount * settings.CREDIT_BACK_PERCENTAGE / 100

    @property
    def dollar_credit_back(self) -> float:
        return get_dollars(self, "credit_back")
