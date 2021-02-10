from typing import Optional

from django.conf import settings
from django.db.transaction import atomic

from billing.choices import InvoicePurpose
from billing.models import Coupon, Invoice
from billing.services.coupon import CouponService
from billing.services.payments import PaymentService
from deliveries.models import Request
from deliveries.services.requests import RequestService
from notifications.tasks import send_email
from orders.choices import OrderPaymentChoices
from orders.containers.order import OrderContainer
from orders.models import Basket, Order
from orders.services.basket import BasketService
from subscriptions.services.subscription import SubscriptionService
from users.models import Client, Employee


class OrderService:
    """
    This service is responsible for TOTAL handling of order:
        - Basket info
        - Delivery info
    """

    def __init__(self, client: Client, order: Order = None):
        self._client = client
        self._order = order

    def checkout(self, order: Order):
        """
        Method to charge all invoices of order.
        At the checkout stage we are creating invoice for every part of Order and
        than charge them:
            - Basket
            - Request (2 Delivery)
            - Subscription
        """

        # TODO REFACTOR

        coupon = order.coupon
        client = self._client
        basket = order.basket
        request = order.request
        subscription = order.subscription
        purpose = InvoicePurpose.ORDER

        services = [
            BasketService(client),
            RequestService(client),
            SubscriptionService(client),
        ]
        objects = [basket, request, subscription]
        real_objects = [item for item in objects if item]

        # 1. we are creating invoices for every service we are offering to client
        # invoices should be created outside of transaction - we are writing explicitly to db
        # if invoices will be inside transaction - when stripe webhook occurs, `.charge` method
        # sometimes doesn't finished.
        for item in services:
            item.refresh_amount_with_discount(
                order=order, basket=basket, request=request, subscription=subscription
            )

        amount = sum([item.amount for item in real_objects])
        discount = sum([item.discount for item in real_objects])

        if subscription:
            purpose = InvoicePurpose.SUBSCRIPTION

        with atomic():
            invoice = Invoice.objects.create(
                client=client,
                amount=amount,
                discount=discount,
                purpose=purpose,
            )
            order.invoice = invoice
            order.save()

            # 2. we are calculating discount for client before charging
            # and persisting them in db
            if coupon:
                self._calculate_and_apply_discount(coupon, invoice)

            # 3. we are charging client for every service and invoices of them
            for item in services:
                item.charge(
                    order=order,
                    basket=basket,
                    request=request,
                    subscription=subscription,
                    invoice=invoice,
                )

            payment_service = PaymentService(client, invoice)
            payment_service.charge()

            # 4. we are calling last hooks
            for item in services:
                item.checkout(
                    order=order, basket=basket, request=request, subscription=subscription
                )

        self._order = order

        return self.get_container()

    def charge_the_rest(self, order: Order):
        """
        We are trying to charge client's prepaid balance and confirm unpaid invoices.
        """

        client = self._client
        invoice = order.invoice

        payment_service = PaymentService(client, invoice)
        payment_service.charge_prepaid_balance()

    def prepare(self, request: Request) -> Order:
        """
        Method prepares Order entity to be ready.
        After this method, we can add items to basket in POS.
        """

        client = self._client

        with atomic():
            # for one order we are creating unique
            # pair of (basket_id, request_id)
            basket, _ = Basket.objects.get_or_create(
                client=client,
                order__request=request,
            )
            order, _ = Order.objects.update_or_create(
                client=client, request=request, defaults={"basket": basket}
            )

        self._order = order

        return order

    def apply_coupon(self, order: Order, coupon: Coupon) -> OrderContainer:
        """
        Method binds coupon with Order.
        """

        # when we link Coupon with Order
        # discount calculated dynamically on the fly inside OrderContainer
        order.coupon = coupon
        order.save()

        self._order = order

        return self.get_container()

    def remove_coupon(self, order: Order) -> OrderContainer:
        """
        Methos remove coupon from Order.
        """

        order.coupon = None
        order.save()

        self._order = order

        return self.get_container()

    def finalize(self, order: Order, employee: Employee) -> Optional[Order]:
        """
        Last hook in payment flow, that marks order as paid and
        calls success events.

        Usually called in 2 cases:
            - If client have enough money and can pay for all our services from prepaid
            balance. Hook called from `POSService`.
            - If client have't money at prepaid balance. In such case this hook will be
            called from `StripeWebhookService`.
        """

        client = self._client
        self._order = order
        invoice = order.invoice

        order.employee = employee
        order.save()

        # we are waiting while all invoices will be confirmed
        if not invoice.is_paid:
            return None

        # if order is paid - no need to fire events again
        if order.payment == OrderPaymentChoices.PAID:
            return None

        with atomic():
            order.payment = OrderPaymentChoices.PAID

            if order.is_save_card:
                order.card = client.main_card

            order.save()

        self._notify_client_on_new_order()

        return order

    def already_formed(self, request: Request) -> Optional[Order]:
        client = self._client
        order = None

        try:
            order = Order.objects.get(client=client, request=request)
        except Order.DoesNotExist:
            pass

        return order

    def fail(self, order: Order):
        """
        Method that handles Stripe Fail Webhook call.
        """

        order.payment = OrderPaymentChoices.FAIL
        order.save()

        self._order = order

        self._notify_client_on_payment_fail()
        self._notify_admin_on_payment_fail()

    def _calculate_and_apply_discount(self, coupon: Coupon, invoice: Invoice):
        amount = invoice.amount

        coupon_service = CouponService(amount, coupon)

        invoice.discount = coupon_service.apply_coupon()
        invoice.save()

    def _notify_client_on_new_order(self):
        client_id = self._client.id
        order_id = self._order.id
        recipient_list = [self._client.email]

        send_email.send(
            event=settings.NEW_ORDER,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
                "order_id": order_id,
            },
        )

    def _notify_client_on_payment_fail(self):
        client_id = self._client.id
        recipient_list = [self._client.email]

        send_email.send(
            event=settings.PAYMENT_FAIL_CLIENT,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
            },
        )

    def _notify_admin_on_payment_fail(self):
        client_id = self._client.id
        order_id = self._order.id
        recipient_list = settings.ADMIN_EMAIL_LIST

        send_email.send(
            event=settings.PAYMENT_FAIL_ADMIN,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
                "order_id": order_id,
            },
        )

    @property
    def order(self):
        order = self._order

        assert (
            order
        ), "Call .checkout or .prepare_subscription_invoices before accessing to .container property"

        return order

    def get_container(self) -> OrderContainer:
        order = self.order
        container = OrderContainer(order)

        return container
