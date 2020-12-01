from typing import List

from django.conf import settings
from django.db.transaction import atomic

from billing.models import Coupon, Invoice
from billing.services.coupon import CouponService
from billing.services.payments import PaymentService
from deliveries.models import Request
from deliveries.services.requests import RequestService
from notifications.tasks import send_email
from orders.choices import PaymentChoices
from orders.containers.order import OrderContainer
from orders.models import Order
from orders.services.basket import BasketService
from subscriptions.services.subscription import SubscriptionService
from users.models import Client


class OrderService:
    """
    This service is responsible for TOTAL handling of order:
        - Basket info
        - Delivery info
    """

    def __init__(self, client: Client, order=None):
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

        coupon = order.coupon

        with atomic():
            # 1. we are creating invoices for every service we are offering to client
            self._create_order_invoices(order)

            order.refresh_from_db()
            invoice_list = order.invoice_list.all()

            # 2. we are calculating discount for client and persisting them in db
            if coupon:
                self._calculate_and_apply_discount(coupon, invoice_list)

            # 3. we are charging client for amount of all invoices
            self._charge_invoices(invoice_list)

        self._order = order

        return self.get_container()

    def prepare(self, request: Request) -> Order:
        """
        Method prepares Order entity to be ready.
        After this method, we can add items to basket in POS.
        """

        client = self._client

        order, _ = Order.objects.get_or_create(
            client=client,
            request=request,
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

    def charge(self, invoice: Invoice):
        """
        We are charging user for:
        - basket amount
        - pickup delivery amount
        - dropoff delivery amount
        """

        payment_service = PaymentService(self._client, invoice)
        payment_service.charge()

    def finalize(self, order: Order) -> Order:
        """
        Last method in payment flow, that marks order as paid and
        calls success events.
        """

        self._order = order

        with atomic():
            order.payment = PaymentChoices.PAID

            if order.is_save_card:
                order.card = self._client.main_card
                order.save()

        self._notify_client_on_new_order()

        return order

    def fail(self, order: Order):
        """
        Method that handles Stripe Fail Webhook call.
        """

        order.payment = PaymentChoices.FAIL
        order.save()

        self._order = order

        self._notify_client_on_payment_fail()
        self._notify_admin_on_payment_fail()

    def _create_order_invoices(self, order: Order):
        client = self._client
        basket = order.basket
        request = order.request
        subscription = order.subscription
        basket_service = BasketService(client)
        request_service = RequestService(client)
        subscription_service = SubscriptionService(client)

        basket_service.create_invoice(order, basket)
        request_service.create_invoice(order, basket, request)
        subscription_service.create_invoice(order, subscription)

    def _calculate_and_apply_discount(self, coupon: Coupon, invoice_list: List[Invoice]):
        for invoice in invoice_list:
            amount = invoice.amount
            coupon_service = CouponService(amount, coupon)
            invoice.discount = coupon_service.apply_coupon()
            invoice.save()

    def _charge_invoices(self, invoice_list: List[Invoice]):
        for invoice in invoice_list:
            self.charge(invoice)

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
