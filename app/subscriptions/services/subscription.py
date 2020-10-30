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
        Based on chosen Package fills Subscription.
        """

        client = self._client

        # TODO refactor
        with atomic():
            subscription, _ = Subscription.objects.get_or_create(
                client=client, invoice__isnull=True, defaults=package.as_dict,
            )
            order, _ = Order.objects.get_or_create(
                client=client,
                subscription=subscription,
                defaults={"status": Status.UNPAID, "is_save_card": True,},
            )

            order_service = OrderService(client, order)
            order_container = order_service.container

            subscription = Subscription.objects.fill_subscription(package, subscription)
            subscription.save()

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
