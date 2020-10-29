from typing import Optional

from django.conf import settings
from django.db.transaction import atomic

from stripe import PaymentMethod

from billing.models import Invoice
from billing.services.card import CardService
from billing.services.payments import PaymentService
from orders.choices import Status
from orders.containers.order import OrderContainer
from orders.models import Order
from orders.services.order import OrderService
from subscriptions.containers import SubscriptionContainer
from subscriptions.models import Package, Subscription
from users.models import Client


class SubscriptionService:
    """
    Used for:
        - Set subscription via `choose`
        - Clone subscription from package
        - Charging user for subscription price
    """

    def __init__(self, client: Client):
        self._client = client
        self._subscription = None

    def choose(self, package: Package) -> OrderContainer:
        """
        Fills Subscription based on Package and creates Order.
        Also, wraps Order in OrderContainer.
        """

        client = self._client
        order_service = OrderService(client)

        with atomic():
            subscription = self._fill_from_package(package)
            order_service.prepare_subscription(subscription)
            order_container = order_service.container

        return order_container

    def checkout(self, order: Order):
        subscription = order.subscription
        invoice_list = order.invoice_list.all()

        with atomic():
            if subscription.name == settings.PAYC:
                self.finalize(order)

            for invoice in invoice_list:
                self.charge(invoice)

    def charge(self, invoice: Invoice) -> Optional[PaymentMethod]:
        """
        For PAYC package we have a special case, where we just store a payment method.
        For other packages - we are charging user for subscription amount.
        """

        payment_service = PaymentService(self._client, invoice)
        card_service = CardService(self._client)

        subscription = invoice.subscription
        payment = None

        if subscription.name == settings.PAYC:
            card = self._client.card_list.first()
            card_service.update_main_card(self._client, card)
            return payment

        payment_service.charge()

    def finalize(self, order: Order) -> Optional[Subscription]:
        """
        Final method that sets subscription on client after payment (checkout).
        """

        subscription = order.subscription

        with atomic():
            order.status = Status.PAID

            if order.is_save_card:
                order.card = self._client.main_card
                order.save()

            self._client.subscription = subscription
            self._client.save()

        return subscription

    @property
    def container(self):
        subscription = self._subscription

        assert subscription, "Call .checkout before accessing to .container property"

        container = SubscriptionContainer(subscription)

        return container

    def _fill_from_package(self, package: Package) -> Subscription:
        """
        Method helps to fill subscription based on package.
        It copies all fields from package to subscription.
        """

        package = package
        client = self._client

        subscription = Subscription(client=client)

        subscription = Subscription.objects.fill_subscription(package, subscription)
        subscription.save()

        self._subscription = subscription

        return subscription
