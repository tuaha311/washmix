import logging
from math import ceil
from typing import Optional, Tuple, Union

from django.conf import settings
from django.db.transaction import atomic

from stripe import PaymentIntent, PaymentMethod, SetupIntent
from stripe.error import StripeError

from billing.choices import InvoiceProvider, InvoicePurpose, WebhookKind
from billing.models import Card, Invoice, Transaction
from billing.services.card import CardService
from billing.stripe_helper import StripeHelper
from billing.utils import create_credit, create_debit, prepare_stripe_metadata
from subscriptions.models import Package, Subscription
from subscriptions.services.subscription import SubscriptionService
from subscriptions.utils import is_advantage_program
from users.models import Client

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Main payment service, that responsible for accepting and providing billing.
    Create a new instance of PaymentService - per one charge.

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
        self.is_fully_paid = False
        self.is_fully_paid_by_credits = False

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
        print("+++IN CHARGE METHOD+++")
        invoice = self._invoice
        client = self._client
        subscription = client.subscription
        subscription_price = (
            subscription.amount_with_discount if subscription else settings.DEFAULT_ZERO_AMOUNT
        )
        is_auto_billing = client.is_auto_billing
        is_subscription_purchase = invoice.purpose == InvoicePurpose.SUBSCRIPTION
        is_advantage = bool(subscription) and is_advantage_program(subscription.name)

        with atomic():
            paid_amount, unpaid_amount = self.charge_prepaid_balance()
            is_order_is_fully_paid = unpaid_amount == 0
            is_subscription_price_enough_for_order_amount = subscription_price >= unpaid_amount

            # most easiest case:
            # client has enough credits to pay for order
            if is_order_is_fully_paid:
                self.is_fully_paid = True
                self.is_fully_paid_by_credits = True

            # simple case:
            # client want to pay for subscription - we are charging for the full price of subscription.
            elif is_subscription_purchase:
                webhook_kind = WebhookKind.SUBSCRIPTION
                continue_with_order = None
                self._process_immediate_payment(webhook_kind, unpaid_amount, continue_with_order)

            # complex case:
            # client doesn't have enough money to pay for POS order with Advantage Program
            # and have `is_auto_billing` option enabled and also Order amount not greater than Subscription price.
            # i.e. for example Order amount is 189$ and Subscription price is 199$ - in such case 1 Subscription
            #  purchase fully cover Order amount and this is the way.
            # we are trying to purchase new subscription and charge rest of money from prepaid balance.
            elif is_auto_billing and is_advantage and is_subscription_price_enough_for_order_amount:
                webhook_kind = WebhookKind.SUBSCRIPTION_WITH_CHARGE
                continue_with_order = invoice.order.pk
                self._process_subscription(webhook_kind, continue_with_order)

            # complex case:
            # client doesn't have enough money to pay for POS order with Advantage Program
            # and have `is_auto_billing` option enabled, but Order amount is higher that subscription price.
            # i.e. Client has a balance 50$, Order amount is 439$ and Subscription price is 199$
            # - in such case we need to charge 50$ from balance, then 240$
            # by one-time payment and purchase Subscription for 199$.
            # we are trying to perform one-time payment refill here, and then in StripeWebhookView we have
            # additional logic that will handle Subscription purchase.
            elif (
                is_auto_billing
                and is_advantage
                and not is_subscription_price_enough_for_order_amount
            ):
                webhook_kind = WebhookKind.REFILL_WITH_CHARGE
                continue_with_order = invoice.order.pk
                self._process_immediate_payment(webhook_kind, unpaid_amount, continue_with_order)

            # complex case:
            # in all other cases, we are trying to refill prepaid balance and charge it.
            else:
                print("--- IN ELSE PART OF PAYMENT.PY 173 ---")
                webhook_kind = WebhookKind.REFILL_WITH_CHARGE
                continue_with_order = invoice.order.pk
                self._process_immediate_payment(webhook_kind, unpaid_amount, continue_with_order)

            if is_advantage and not is_auto_billing and client.balance <= 0:
                package = Package.objects.get(name=settings.PAYC)
                subscription = Subscription.objects.fill_subscription(package, subscription)
                subscription.save()
                client.subscription = subscription
                client.save()

    def charge_subscription_with_auto_billing(self):
        """
        Check client balance and purchase Subscription if balance is lower than AUTO_BILLING_LIMIT
        """

        client = self._client
        subscription = client.subscription
        is_auto_billing = client.is_auto_billing
        is_need_to_auto_bill = client.balance < settings.AUTO_BILLING_LIMIT
        is_advantage = bool(subscription) and is_advantage_program(subscription.name)

        # after client paid for his order, we should purchase subscription
        #  if he has a Advantage Program with `is_auto_billing` option enabled
        if is_auto_billing and is_advantage and is_need_to_auto_bill:
            webhook_kind = WebhookKind.SUBSCRIPTION
            continue_with_order = None
            self._process_subscription(webhook_kind, continue_with_order)

    def charge_prepaid_balance(self):
        """
        Method that charges user's prepaid balance.
        """
        print("+++ IN CHARGE PREPAID BALANCE +++")
        client = self._client
        invoice = self._invoice
        paid_amount, unpaid_amount = self._calculate_prepaid_and_card_charge()

        if paid_amount > 0:
            create_credit(
                client=client,
                invoice=invoice,
                amount=paid_amount,
            )

        return paid_amount, unpaid_amount

    def _process_subscription(self, webhook_kind: str, continue_with_order: Optional[int]):
        """
        Method that helps to buy subscription if user doesn't have enough
        prepaid balance.

        Used in cases:
            - If client fully paid for order, but have a balance lower than < 20$.
            - If client doesn't fully paid for order and has option `is_auto_billing` = True and we
            need to buy subscription and then finish our order.
        """

        request = None
        basket = None
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

        amount = ceil(invoice.amount_with_discount)
        self._charge_card(
            amount=amount,
            webhook_kind=webhook_kind,
            invoice=invoice,
            continue_with_order=continue_with_order,
        )

        subscription_service.checkout(order=subscription_order, subscription=subscription)

    def _process_immediate_payment(
        self, webhook_kind: str, unpaid_amount: int, continue_with_order: Optional[int]
    ):
        """
        Method helps to charge client's card with one time payment.

        This method called in cases:
            - Always for PAYC.
            - For GOLD and PLATINUM when they have `is_auto_billing` = False.
            - Only Subscription purchase.
        """
        print("+++ IN _process_immediate_payment +++")
        client = self._client

        if webhook_kind == WebhookKind.REFILL_WITH_CHARGE:
            print("---   webhook_kind == WebhookKind.REFILL_WITH_CHARGE -----")
            invoice = Invoice.objects.create(
                client=client,
                amount=unpaid_amount,
                discount=settings.DEFAULT_ZERO_DISCOUNT,
                purpose=InvoicePurpose.ONE_TIME_PAYMENT,
            )
        else:
            invoice = self._invoice

        amount = ceil(invoice.amount_with_discount)
        print("AMOUNT:      ", amount)
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
        print("---- IN CHARGE CARD:     ----")
        payment = None

        for card in self._client.card_list.all():
            # we are trying to charge the card list of client
            # and we are stopping at first successful attempt

            try:
                print("IN CARD LOOP IN CHARGE CARD:     ", card.__dict__)
            except:
                pass

            if self.is_fully_paid:
                break

            try:
                metadata = prepare_stripe_metadata(
                    invoice_id=invoice.id,
                    webhook_kind=webhook_kind,
                    continue_with_order=continue_with_order,
                )

                print("^^^ IN prepare_stripe_metadata ^^^     ", metadata)

                payment = self._stripe_helper.create_payment_intent(
                    payment_method_id=card.stripe_id,
                    amount=amount,
                    metadata=metadata,
                )
                self._save_card(invoice=invoice, card=card)

                self.is_fully_paid = True

            except StripeError as err:
                print("GOT SOME ERROR HERE ", err)
                logger.error(err)
                continue

        return payment

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
        try:
            print("IN _calculate_prepaid_and_card_charge,     ", invoice.__dict__)
        except:
            pass

        amount_with_discount = invoice.amount_with_discount #1990
        paid_amount = invoice.paid_amount
        print("PAID AMOUNT:        ", paid_amount)
        unpaid_amount = amount_with_discount - paid_amount
        print("UNPAID AMOUNT:      ", unpaid_amount)
        balance = client.balance

        prepaid_balance_will_be_charged = 0
        card_will_be_charged = amount_with_discount - prepaid_balance_will_be_charged

        # for subscription we are always charging card by full price
        # without charging prepaid balance
        if invoice.purpose == InvoicePurpose.SUBSCRIPTION:
            print('++++ AAAAAAAAAA ++++++')
            prepaid_balance_will_be_charged = 0
            card_will_be_charged = ceil(invoice.amount_with_discount)

            # we are ceiling to a integer number for Stripe
            return prepaid_balance_will_be_charged, card_will_be_charged

        # if prepaid balance enough to pay full price - we will
        # use this money for invoice payment.
        if balance >= unpaid_amount:
            print('++++ BBBBBBBBBBBB ++++++')
            prepaid_balance_will_be_charged = unpaid_amount
            card_will_be_charged = 0

        # but if our prepaid balance is lower that rest of unpaid invoice amount -
        # we charge all of prepaid balance and rest of unpaid invoice amount
        # we should charge it from card
        elif 0 < balance < unpaid_amount:
            print('++++ CCCCCCCCCCC ++++++')
            prepaid_balance_will_be_charged = balance
            card_will_be_charged = ceil(unpaid_amount - balance)

        print('++++ prepaid_balance_will_be_charged  ++++++    ', prepaid_balance_will_be_charged)
        print('')
        print('++++ card_will_be_charged  ++++++    ', card_will_be_charged)
        # we are ceiling to a integer number for Stripe
        return prepaid_balance_will_be_charged, card_will_be_charged
