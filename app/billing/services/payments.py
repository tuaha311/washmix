import logging
from typing import Optional, Tuple, Union

from django.conf import settings
from django.db.transaction import atomic

from rest_framework import serializers
from stripe import PaymentIntent, PaymentMethod, SetupIntent
from stripe.error import StripeError

from billing.choices import InvoiceProvider, InvoicePurpose, WebhookKind
from billing.models import Card, Invoice, Transaction
from billing.services.card import CardService
from billing.stripe_helper import StripeHelper
from billing.utils import create_credit, create_debit, get_webhook_kind, prepare_stripe_metadata
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
            metadata = prepare_stripe_metadata(
                invoice_id=invoice.id,
                webhook_kind=webhook_kind,
                continue_with_order=None,
            )
            intent = self._stripe_helper.create_payment_intent(
                amount=amount,
                metadata=metadata,
            )

        return intent

    def confirm(
        self, payment: PaymentMethod, provider=InvoiceProvider.STRIPE
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
        client = self._client
        subscription = client.subscription
        is_auto_billing = client.is_auto_billing
        is_advantage = bool(subscription) and (
            subscription.name in [settings.GOLD, settings.PLATINUM]
        )

        with atomic():
            paid_amount, unpaid_amount = self.charge_prepaid_balance()
            is_need_to_auto_bill = client.balance < settings.AUTO_BILLING_LIMIT

            if unpaid_amount == 0:
                return None

            # if Client doesn't have enough prepaid balance - we should charge
            # their card or purchase subscription
            if is_auto_billing and is_advantage:
                webhook_kind = WebhookKind.SUBSCRIPTION_WITH_CHARGE
                self._make_subscription_with_charge(webhook_kind)
            else:
                webhook_kind = get_webhook_kind(invoice)
                self._make_refill_with_charge(webhook_kind)

    def charge_prepaid_balance(self):
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

    def _make_subscription_with_charge(self, webhook_kind: str):
        """
        Method that helps to buy subscription if user doesn't have enough
        prepaid balance.
        """

        request = None
        basket = None
        original_invoice = self._invoice
        continue_with_order = original_invoice.order.pk
        client = self._client
        subscription = client.subscription
        subscription_name = subscription.name
        package = Package.objects.get(name=subscription_name)

        with atomic():
            # we are manually handling subscription purchase proccess
            subscription_service = SubscriptionService(client)
            order_container = subscription_service.choose(package)

            subscription_order = order_container.original
            subscription = subscription_order.subscription

            subscription_service.refresh_amount_with_discount(
                order=subscription_order, basket=basket, request=request, subscription=subscription
            )

            invoice = Invoice.objects.create(
                client=client,
                amount=subscription.amount,
                discount=subscription.discount,
                purpose=InvoicePurpose.SUBSCRIPTION,
            )
            subscription_order.invoice = invoice
            subscription_order.save()

        amount = int(invoice.amount_with_discount)
        self._charge_card(
            amount=amount,
            webhook_kind=webhook_kind,
            invoice=invoice,
            continue_with_order=continue_with_order,
        )

        subscription_service.checkout(order=subscription_order, subscription=subscription)

    def _make_refill_with_charge(self, webhook_kind: str):
        """
        Method helps to charge client's card with one time payment.
        """

        continue_with_order = None
        original_invoice = self._invoice
        invoice = original_invoice

        if webhook_kind == WebhookKind.REFILL_WITH_CHARGE:
            # we are preparing invoice for one time payment
            # without linking to order
            # this invoice will receive Stripe income transaction
            invoice = Invoice.objects.create(
                client=original_invoice.client,
                amount=original_invoice.amount,
                discount=original_invoice.discount,
                purpose=InvoicePurpose.ONE_TIME_PAYMENT,
            )
            # we are saving original order to continue with it
            # in `StripeWebhookView`
            continue_with_order = original_invoice.order.pk

        amount = int(invoice.amount_with_discount)
        self._charge_card(
            amount=amount,
            webhook_kind=webhook_kind,
            invoice=invoice,
            continue_with_order=continue_with_order,
        )

    def _charge_card(
        self, amount: int, webhook_kind: str, invoice: Invoice, continue_with_order: int
    ):
        """
        Method that tries to charge money from user's card.
        """

        charge_successful = False
        payment = None

        for card in self._client.card_list.all():
            # we are trying to charge the card list of client
            # and we are stopping at first successful attempt

            if charge_successful:
                break

            try:
                metadata = prepare_stripe_metadata(
                    invoice_id=invoice.id,
                    webhook_kind=webhook_kind,
                    continue_with_order=continue_with_order,
                )
                payment = self._stripe_helper.create_payment_intent(
                    payment_method_id=card.stripe_id,
                    amount=amount,
                    metadata=metadata,
                )
                self._save_card(invoice=invoice, card=card)

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

    def _get_aggregated_invoice(self):
        pass

    def _save_card(self, invoice: Invoice, card: Card):
        """
        Save card to client and into invoice.
        """

        card_service = CardService(self._client)
        card_service.update_main_card(self._client, card)

        invoice.card = card
        invoice.save()

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
