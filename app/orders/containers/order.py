from typing import List, Optional

from django.conf import settings

from billing.services.coupon import CouponService
from core.containers import BaseAmountContainer
from core.utils import get_dollars
from deliveries.containers.request import RequestContainer
from orders.containers.basket import BasketContainer
from orders.models import Order
from subscriptions.containers import SubscriptionContainer


class OrderContainer(BaseAmountContainer):
    proxy_to_object = "_order"

    def __init__(self, order: Order):
        self._order = order

    @property
    def amount(self) -> int:
        filled_container_list = self._filled_container_list
        request = self.request
        rush_amount = [request.rush_amount]

        amount_list = [item.amount for item in filled_container_list]
        amount_with_rush = amount_list + rush_amount

        total_amount = sum(amount_with_rush)

        return total_amount

    @property
    def discount(self) -> int:
        order = self._order
        coupon = order.coupon
        coupon_discount = 0

        if coupon:
            amount = self.amount
            coupon_service = CouponService(amount, coupon)
            coupon_discount = coupon_service.apply_coupon()

        filled_container_list = self._filled_container_list
        subscription_discount_list = [item.discount for item in filled_container_list]
        subscription_discount = sum(subscription_discount_list)

        return subscription_discount + coupon_discount

    @property
    def credit_back(self) -> int:
        amount_with_discount = self.amount_with_discount

        return amount_with_discount * settings.CREDIT_BACK_PERCENTAGE / 100

    @property
    def dollar_credit_back(self) -> float:
        return get_dollars(self, "credit_back")

    @property
    def basket(self) -> Optional[BasketContainer]:
        order = self._order
        client = order.client
        subscription = client.subscription
        basket = order.basket

        if not basket:
            return None

        container = BasketContainer(subscription, basket)

        return container

    @property
    def request(self) -> Optional[RequestContainer]:
        order = self._order
        client = order.client
        subscription = client.subscription
        request = order.request
        basket = order.basket

        if not request or not basket:
            return None

        basket_container = BasketContainer(subscription, basket)
        request_container = RequestContainer(subscription, request, basket_container)

        return request_container

    @property
    def subscription(self) -> Optional[SubscriptionContainer]:
        order = self._order
        subscription = order.subscription

        if not subscription:
            return None

        subscription_container = SubscriptionContainer(subscription)

        return subscription_container

    @property
    def _filled_container_list(self) -> List:
        basket_container = self.basket
        request_container = self.request
        subscription_container = self.subscription

        container_list = [basket_container, request_container, subscription_container]
        filled_container_list = [item for item in container_list if item]

        return filled_container_list
