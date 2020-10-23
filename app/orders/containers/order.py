from django.db.models import Sum

from core.containers import BaseAmountContainer
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

        amount = invoice_list.aggregate(total=Sum("amount")) or 0

        return amount

    @property
    def discount(self) -> int:
        order = self._order
        invoice_list = order.invoice_list.all()

        amount = invoice_list.aggregate(total=Sum("discount")) or 0

        return amount
