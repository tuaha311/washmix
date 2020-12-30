from typing import List, Optional
from uuid import uuid4

from django.conf import settings
from django.db.transaction import atomic

from billing.choices import Provider, Purpose
from billing.containers import PaymentContainer
from billing.models import Invoice
from billing.services.card import CardService
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from core.interfaces import PaymentInterfaceService
from deliveries.models import Request
from notifications.tasks import send_email
from orders.choices import PaymentChoices, StatusChoices
from orders.containers.order import OrderContainer
from orders.models import Basket, Order
from subscriptions.containers import SubscriptionContainer
from subscriptions.models import Package, Subscription
from users.models import Client


class SubscriptionService(PaymentInterfaceService):
    """
    Used for:
        - Set subscription via `choose`
        - Clone subscription from package
        - Charging user for subscription price
    """

    def __init__(self, client: Client):
        self._client = client

    def create_invoice(
        self,
        order: Order,
        basket: Optional[Basket],
        request: Optional[Request],
        subscription: Optional[Subscription],
        **kwargs,
    ) -> Optional[List[Invoice]]:
        """
        Creates invoice for subscription. Called on Welcome checkout.
        """

        if not subscription:
            return None

        client = self._client
        invoice_service = InvoiceService(client)
        subscription_container = SubscriptionContainer(subscription)

        subscription_invoice = invoice_service.update_or_create(
            order=order,
            amount=subscription_container.amount,
            discount=subscription_container.discount,
            purpose=Purpose.SUBSCRIPTION,
        )

        subscription.invoice = subscription_invoice
        subscription.save()

        return [subscription_invoice]

    def charge(
        self,
        request: Optional[Request],
        basket: Optional[Basket],
        subscription: Optional[Subscription],
        **kwargs,
    ):
        """
        For PAYC package we have a special case, where we just store a payment method.
        For other packages - we are charging user for subscription amount.
        """

        if not subscription:
            return None

        invoice = subscription.invoice
        client = self._client
        payment_service = PaymentService(client, invoice)
        card_service = CardService(client)

        # save payment method for PAYC
        # and confirm payment
        if subscription.name == settings.PAYC:
            card = client.card_list.first()
            card_service.update_main_card(client, card)

            payment_id = str(uuid4())
            payment_amount = 0
            payment_container = PaymentContainer(payment_id, payment_amount)

            payment_service.confirm(payment_container, provider=Provider.WASHMIX)
        else:
            payment_service.charge()

    def checkout(self, order: Order, subscription: Subscription, **kwargs):
        """
        Method has additional handling for PAYC packages.

        This method called in OrderService.checkout and we are passing a
        few extra kwargs.
        """

        if not subscription:
            return None

        if subscription.name == settings.PAYC:
            self.finalize(order)

    def choose(self, package: Package) -> OrderContainer:
        """
        Action for Subscription, clones all properties of Subscription
        based on Package attributes.
        """

        with atomic():
            subscription = self._get_or_create_subscription(package)
            order_service = self._get_order_service(subscription)

            subscription = Subscription.objects.fill_subscription(package, subscription)
            subscription.save()

        return order_service.get_container()

    def finalize(self, order: Order) -> Optional[Subscription]:
        """
        Final method that sets subscription on client after payment (checkout).
        """

        subscription = order.subscription

        with atomic():
            order.payment = PaymentChoices.PAID

            if order.is_save_card:
                order.card = self._client.main_card
                order.save()

            self._client.subscription = subscription
            self._client.save()

        self._notify_client_on_purchase_of_advantage_program(subscription)

        return subscription

    def fail(self, order: Order):
        subscription = order.subscription

        order_service = self._get_order_service(subscription)
        order_service.fail(order)

    def _notify_client_on_purchase_of_advantage_program(self, subscription: Subscription):
        client_id = self._client.id
        subscription_id = subscription.id
        recipient_list = [self._client.email]

        if subscription.name not in [settings.GOLD, settings.PLATINUM]:
            return None

        send_email.send(
            event=settings.PURCHASE_SUBSCRIPTION_GOLD_PLATINUM,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
                "subscription_id": subscription_id,
            },
        )

    def _get_order_service(self, subscription: Subscription):
        # We are preventing circular import of OrderService
        # by importing this import inline
        from orders.services.order import OrderService

        client = self._client

        # we are looking for last order, that was created for subscription
        # and wasn't paid
        order, _ = Order.objects.get_or_create(
            client=client,
            subscription=subscription,
            defaults={
                "status": StatusChoices.ACCEPTED,
                "payment": PaymentChoices.UNPAID,
                "is_save_card": True,
            },
        )
        order_service = OrderService(client, order)

        return order_service

    def _get_or_create_subscription(self, package: Package):
        client = self._client

        # we are looking for last subscription that wasn't attached to the client.
        subscription, _ = Subscription.objects.get_or_create(
            client=client,
            active_client__isnull=True,
            defaults={"invoice": None, **package.as_dict},
        )

        return subscription
