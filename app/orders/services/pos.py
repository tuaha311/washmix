from typing import Optional

from django.conf import settings
from django.db.transaction import atomic

from orders.containers.order import OrderContainer
from orders.models import Order
from orders.services.order import OrderService
from subscriptions.models import Package
from subscriptions.services.subscription import SubscriptionService
from users.models import Client, Employee


class POSService:
    def __init__(self, client: Client, order: Order, employee: Employee):
        self._client = client
        self._order = order
        self._employee = employee

    def checkout(self) -> OrderContainer:
        """
        If balance is enough:
            - charging prepaid balance
        If not and client has enabled `is_auto_billing` option:
            - purchase a new subscription
            - charging prepaid balance
        if not and client has disabled `is_auto_billing` option:
            - charging prepaid balance
            - trying to charge card on unpaid amount from card
        """

        client = self._client

        if not self._is_enough_balance and client.is_auto_billing:
            self._purchase_subscription()

        order_container = self._pay_for_order()

        return order_container

    def _pay_for_order(self) -> OrderContainer:
        """
        Handler that responsible for default POS workflow.
        """

        client = self._client
        order = self._order
        employee = self._employee

        order_service = OrderService(client)
        order_container = order_service.checkout(order)
        order_service.finalize(order, employee)

        return order_container

    def _purchase_subscription(self) -> Optional[OrderContainer]:
        """
        Fallback handler that responsible for case, when user
        doesn't have enough prepaid balance to pay for order.
        """

        client = self._client
        subscription = client.subscription
        subscription_name = subscription.name
        package = Package.objects.get(name=subscription_name)

        # at PAYC subscription we can't have prepaid balance and
        # subscription purchase doesn't give to us anything
        if subscription_name == settings.PAYC:
            return None

        with atomic():
            subscription_service = SubscriptionService(client)
            order_container = subscription_service.choose(package)
            order = order_container.original

            order_service = OrderService(client, order)
            order_container = order_service.checkout(order)

        return order_container

    @property
    def _is_enough_balance(self) -> bool:
        """
        Checks is balance enough to pay for POS order.
        """

        client = self._client
        order = self._order
        order_container = OrderContainer(order)

        is_enough_balance = client.balance > order_container.amount_with_discount

        return is_enough_balance
