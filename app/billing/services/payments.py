import logging
from typing import Optional, Tuple, Union

from django.conf import settings
from django.db.transaction import atomic

from rest_framework import serializers
from stripe import PaymentIntent, PaymentMethod, SetupIntent
from stripe.error import StripeError

from billing.choices import InvoiceProvider, InvoicePurpose, WebhookKind
from billing.containers import PaymentContainer
from billing.models import Invoice, Transaction
from billing.services.card import CardService
from billing.stripe_helper import StripeHelper
from billing.utils import create_credit, create_debit
from orders.containers.order import OrderContainer
from orders.models import Order
from subscriptions.models import Package
from subscriptions.services.subscription import SubscriptionService
from users.models import Client

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Main payment service, that responsible for accepting and providing billing.

    This service main core capabilities:
        - Save user's card in Stripe
        - Charge user's card immediately
        - Charge user's card later
        - Confirm payment
    """

    def __init__(self, client: Client, invoice: Invoice):
        self._client = client
        self._invoice = invoice
        self._stripe_helper = StripeHelper(client)

    def create_intent(
        self,
        is_save_card: bool,
        webhook_kind: str,
    ) -> Union[SetupIntent, PaymentIntent]:
        """
        This method used to create Stripe's `SetupIntent` or `PaymentIntent` in
        dependency of user preferences:
            - If user want to save card, we create `SetupIntent` to save user's card
            in Stripe and for later billing
            - If user want to make one time payment - we are creating immediate payment entity
            called `PaymentIntent`
        """

        invoice = self._invoice
        amount = invoice.amount_with_discount

        if is_save_card:
            intent = self._stripe_helper.create_setup_intent()
        else:
            intent = self._stripe_helper.create_payment_intent(
                amount=amount,
                invoice=invoice,
                webhook_kind=webhook_kind,
            )

        return intent

    def confirm(
        self, payment: Union[PaymentMethod, PaymentContainer], provider=InvoiceProvider.STRIPE
    ) -> Optional[Transaction]:
        """
        Last method in payment flow - it's responsible for creating payment transaction
        for invoice. After transaction created for invoice, Invoice will be marked
        as paid.
        """

        invoice = self._invoice

        # .confirm method works idempotently - if we already marked
        # invoice as paid, than we doesn't make changes.
        # also we are checking that invoice has a transaction - special case for PAYC
        # when invoice has amount of 0.
        if invoice.is_paid and invoice.has_transaction:
            return None

        transaction = create_debit(
            client=self._client,
            invoice=self._invoice,
            stripe_id=payment.id,
            amount=payment.amount,
            source=payment,
            provider=provider,
        )

        return transaction

    def charge(self):
        """
        We are iterating via all user's card list and choosing first one
        where we find an enough money to charge. At first successful attempt we
        are continuing our payment flow.

        In most cases, we are creating `PaymentIntent` under the hood and then waiting for
        web hook event from Stripe to confirm and finish payment flow.
        """

        invoice = self._invoice
        parent_order = invoice.order
        client = self._client
        webhook_kind = WebhookKind.REFILL_WITH_CHARGE
        subscription = client.subscription
        is_auto_billing = client.is_auto_billing
        is_advantage = bool(subscription) and (
            subscription.name in [settings.GOLD, settings.PLATINUM]
        )

        # for subscription we are always set corresponding webhook kind
        if invoice.purpose == InvoicePurpose.SUBSCRIPTION:
            webhook_kind = WebhookKind.SUBSCRIPTION

        with atomic():
            paid_amount, unpaid_amount = self._charge_prepaid_balance()

            if unpaid_amount == 0:
                return None

            # if Client doesn't have enough prepaid balance - we should charge
            # their card or purchase subscription
            if is_auto_billing and is_advantage:
                child_order, webhook_kind = self._purchase_subscription_with_charge()
            else:
                child_order, webhook_kind = self._charge_card(
                    amount=unpaid_amount, webhook_kind=webhook_kind, invoice=invoice
                )

            # let's save a parent order - order that created current child order
            # we will refer and use this value later in `StripeWebhookView`
            if webhook_kind in [
                WebhookKind.SUBSCRIPTION_WITH_CHARGE,
                WebhookKind.REFILL_WITH_CHARGE,
            ]:
                child_order.parent = parent_order
                child_order.save()

    def _charge_prepaid_balance(self):
        """
        Method that charges user's prepaid balance.
        """

        client = self._client
        invoice = self._invoice
        charge_from_prepaid, charge_from_card = self._calculate_prepaid_and_card_charge()

        if charge_from_prepaid > 0:
            create_credit(
                client=client,
                invoice=invoice,
                amount=charge_from_prepaid,
            )

        return charge_from_prepaid, charge_from_card

    def _charge_card(self, amount: int, webhook_kind: str, invoice: Invoice):
        """
        Method that tries to charge money from user's card.
        """

        card_service = CardService(self._client)
        charge_successful = False
        payment = None

        for item in self._client.card_list.all():
            # we are trying to charge the card list of client
            # and we are stopping at first successful attempt

            if charge_successful:
                break

            try:
                payment = self._stripe_helper.create_payment_intent(
                    payment_method_id=item.stripe_id,
                    amount=amount,
                    invoice=invoice,
                    webhook_kind=webhook_kind,
                )
                card_service.update_main_card(self._client, item)

                invoice.card = item
                invoice.save()

                charge_successful = True

            except StripeError as err:
                logger.error(err)
                continue

        if not charge_successful:
            raise serializers.ValidationError(
                detail="Can't bill your card.",
                code="cant_bill_your_card",
            )

        return payment

    def _purchase_subscription_with_charge(self) -> Tuple[Order, str]:
        """
        Method that helps to buy subscription if user doesn't have enough
        prepaid balance.
        """

        request = None
        basket = None
        client = self._client
        subscription = client.subscription
        subscription_name = subscription.name
        webhook_kind = WebhookKind.SUBSCRIPTION_WITH_CHARGE
        package = Package.objects.get(name=subscription_name)

        with atomic():
            # we are manually handling subscription purchase proccess
            subscription_service = SubscriptionService(client)
            order_container = subscription_service.choose(package)

            order = order_container.original
            subscription = order.subscription
            amount = subscription.price

            # 1. creating invoice with list unpacking
            # 2. charging the card with purpose=POS to indicate that we are processing POS case
            # 3. calling final hooks
            [invoice] = subscription_service.create_invoice(
                order=order, basket=basket, request=request, subscription=subscription
            )
            self._charge_card(amount=amount, webhook_kind=webhook_kind, invoice=invoice)
            subscription_service.checkout(order=order, subscription=subscription)

        return order, webhook_kind

    def _calculate_prepaid_and_card_charge(self) -> Tuple[int, int]:
        """
        Method that calculates:
            - prepaid balance that can be charged
            - card charge amount
        """

        invoice = self._invoice
        client = self._client

        amount_with_discount = invoice.amount_with_discount
        paid_amount = invoice.paid_amount
        unpaid_amount = amount_with_discount - paid_amount
        balance = client.balance

        prepaid_balance_will_be_charged = 0
        card_will_be_charged = amount_with_discount - prepaid_balance_will_be_charged

        # for subscription we are always charging card by full price
        # without charging prepaid balance
        if invoice.purpose == InvoicePurpose.SUBSCRIPTION:
            prepaid_balance_will_be_charged = 0
            card_will_be_charged = invoice.amount_with_discount

            # we are reducing to a integer number for Stripe
            return prepaid_balance_will_be_charged, int(card_will_be_charged)

        # if prepaid balance enough to pay full price - we will
        # use this money for invoice payment.
        if balance >= unpaid_amount:
            prepaid_balance_will_be_charged = unpaid_amount
            card_will_be_charged = 0

        # but if our prepaid balance is lower that rest of unpaid invoice amount -
        # we charge all of prepaid balance and rest of unpaid invoice amount
        # we should charge it from card
        elif 0 < balance < unpaid_amount:
            prepaid_balance_will_be_charged = balance
            card_will_be_charged = unpaid_amount - balance

        # we are reducing to a integer number for Stripe
        return prepaid_balance_will_be_charged, int(card_will_be_charged)
