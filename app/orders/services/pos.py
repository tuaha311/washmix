from typing import Optional

from rest_framework import serializers

from billing.models import Invoice
from billing.services.payments import PaymentService
from orders.containers.order import OrderContainer
from orders.models import Order
from orders.services.order import OrderService
from users.models import Client, Employee


class POSService:
    """
    POS service that handles orders.
    """

    def __init__(
        self,
        client: Client,
        order: Order,
        employee: Optional[Employee],
        invoice: Optional[Invoice] = None,
    ):
        self._client = client
        self._order = order
        self._employee = employee
        self._invoice = invoice

    def checkout(self) -> OrderContainer:
        """
        Method that finishes created order in POS after new subscription purchase +
        pays for the rest of order.
        """

        client = self._client
        order = self._order
        employee = self._employee

        order_service = OrderService(client)
        order_container, charge_succesful = order_service.checkout(order)

        if not charge_succesful:
            raise serializers.ValidationError(
                detail="Can't bill your card",
                code="cant_bill_your_card",
            )

        order_service.finalize(order, employee)

        return order_container

    def charge_the_rest(self):
        """
        Method that finishes created order in POS after one time payment +
        pays for the rest of order.
        """

        client = self._client
        order = self._order
        employee = self._employee

        order_service = OrderService(client)
        order_service.charge_the_rest(order)
        order_service.finalize(order, employee)

    def check_balance_and_purchase_subscription(self):
        """
        Check client's balance.
        """

        client = self._client
        invoice = self._invoice

        payment_service = PaymentService(client, invoice)
        payment_service.check_balance_and_purchase_subscription()
