from typing import Optional

from django.conf import settings
from django.db.transaction import atomic

from billing.choices import InvoiceProvider
from billing.models import Invoice
from billing.services.card import CardService
from billing.services.invoice import InvoiceService
from billing.utils import confirm_debit, create_debit
from core.interfaces import PaymentInterfaceService
from deliveries.models import Request
from notifications.tasks import send_email
from orders.choices import OrderPaymentChoices, OrderStatusChoices
from orders.containers.order import OrderContainer
from orders.models import Basket, Order
from subscriptions.containers import SubscriptionContainer
from subscriptions.models import Package, Subscription
from subscriptions.utils import get_direction_of_subscription, is_advantage_program
from users.models import Client


class SubscriptionService(PaymentInterfaceService):
    """
    Used for:
        - Set subscription via `choose`
        - Clone subscription from package
        - Charging user for subscription price

    Order of methods by importance:
        - refresh_amount_with_discount
        - charge
        - checkout
        - finalize
    """

    def __init__(self, client: Client):
        self._client = client

    def refresh_amount_with_discount(
        self,
        order: Order,
        basket: Optional[Basket],
        request: Optional[Request],
        subscription: Optional[Subscription],
        **kwargs,
    ) -> Optional[float]:
        """
        Creates invoice for subscription. Called on Welcome checkout.
        """

        if not subscription:
            return None

        client = self._client
        invoice_service = InvoiceService(client)
        subscription_container = SubscriptionContainer(subscription)

        subscription = invoice_service.refresh_amount_discount(
            entity=subscription,
            amount=subscription_container.amount,
            discount=subscription_container.discount,
        )

        return subscription.amount_with_discount

    def confirm(
        self,
        request: Optional[Request],
        basket: Optional[Basket],
        subscription: Optional[Subscription],
        invoice: Invoice,
        **kwargs,
    ):
        """
        For PAYC package we have a special case, where we just store a payment method.
        For other packages - we are charging user for subscription amount.
        """

        if not subscription:
            return None

        client = self._client
        card_service = CardService(client)
        is_advantage = is_advantage_program(subscription.name)

        # confirm invoice for PAYC and if invoice doesn't have transactions
        if not is_advantage and not invoice.has_transaction:
            card = client.card_list.first()
            card_service.update_main_card(client, card)
            confirm_debit(client, invoice)

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

    def finalize(self, order: Order, is_replenished: bool = False) -> Optional[Subscription]:
        """
        Final hook that sets subscription on client after payment (checkout).

        Usually called in 2 cases:
            - If user purchases PAYC subscription. PAYC is free and doesn't require any charges.
            In such case will be called by self (`SubscriptionService`).
            - If user purchases GOLD or PLATINUM subscription. Then it will be called inside `StripeWebhookService`.

        If subscription processed with discount (for example, client purchases GOLD for 189$ instead of 199$ -
        discount 10$) we should add 10$ of discount as credit balance.
        """

        client = self._client
        future_subscription = order.subscription
        old_subscription = client.subscription
        invoice = order.invoice

        # we are waiting while all invoices will be confirmed
        if not invoice.is_paid:
            return None

        # if order is paid - no need to fire events again
        if order.payment == OrderPaymentChoices.PAID:
            return None

        with atomic():
            order.payment = OrderPaymentChoices.PAID
            order.status = OrderStatusChoices.COMPLETED

            if order.is_save_card:
                order.card = client.main_card

            order.save()

            client.subscription = future_subscription
            client.save()

            if invoice.discount:
                amount = invoice.discount
                create_debit(
                    client=client, invoice=invoice, amount=amount, provider=InvoiceProvider.WASHMIX
                )

        self._notify_client_on_purchase_of_advantage_program(
            old_subscription, future_subscription, is_replenished
        )

        return future_subscription

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

    def fail(self, order: Order):
        subscription = order.subscription

        order_service = self._get_order_service(subscription)
        order_service.fail(order)

    def _notify_client_on_purchase_of_advantage_program(
        self,
        old_subscription: Optional[Subscription],
        future_subscription: Subscription,
        is_replenished: bool,
    ):
        client_id = self._client.id
        subscription_id = future_subscription.id
        recipient_list = [self._client.email]
        is_first_purchase = old_subscription is None
        is_advantage = is_advantage_program(future_subscription.name)
        is_payc = not is_advantage
        direction_of_subscription = get_direction_of_subscription(
            old_subscription,
            future_subscription,
            is_replenished,
        )

        # we don't sent any email if this is a first purchase and
        # client purchased a PAYC
        if is_first_purchase and is_payc:
            return None

        send_email.send(
            event=settings.PURCHASE_SUBSCRIPTION,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
                "subscription_id": subscription_id,
                "direction_of_subscription": direction_of_subscription,
                "is_advantage": is_advantage,
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
                "status": OrderStatusChoices.ACCEPTED,
                "payment": OrderPaymentChoices.UNPAID,
                "is_save_card": True,
            },
        )
        order_service = OrderService(client, order)

        return order_service

    def _get_or_create_subscription(self, package: Package):
        client = self._client

        # we are looking for last subscription that wasn't attached to the client
        # and wasn't prepared for payment
        subscription, _ = Subscription.objects.get_or_create(
            client=client,
            order__invoice__isnull=True,
            active_client__isnull=True,
            defaults=package.as_dict,
        )

        return subscription
