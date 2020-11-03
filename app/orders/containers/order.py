from typing import Optional

from django.conf import settings
from django.db.models import Sum

from core.containers import BaseAmountContainer
from core.utils import get_dollars
from deliveries.containers.request import RequestContainer
from orders.containers.basket import BasketContainer
from orders.models import Order


class OrderContainer(BaseAmountContainer):
    proxy_to_object = "_order"

    def __init__(self, order: Order):
        self._order = order

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
    def amount(self) -> int:
        order = self._order
        invoice_list = order.invoice_list.all()

        amount = invoice_list.aggregate(total=Sum("amount"))["total"] or 0

        return amount

    @property
    def discount(self) -> int:
        order = self._order
        invoice_list = order.invoice_list.all()

        amount = invoice_list.aggregate(total=Sum("discount"))["total"] or 0

        return amount

    @property
    def credit_back(self) -> int:
        amount_with_discount = self.amount_with_discount

        return amount_with_discount * settings.CREDIT_BACK_PERCENTAGE / 100

    @property
    def dollar_credit_back(self) -> float:
        return get_dollars(self, "credit_back")
