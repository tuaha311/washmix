from typing import List

from django.conf import settings
from django.db.transaction import atomic

from billing.models import Coupon, Invoice
from billing.services.coupon import CouponService
from deliveries.models import Request
from deliveries.services.requests import RequestService
from notifications.tasks import send_email
from orders.choices import PaymentChoices
from orders.containers.order import OrderContainer
from orders.models import Basket, Order
from orders.services.basket import BasketService
from orders.tasks import generate_pdf_from_html
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
        client = self._client
        basket = order.basket
        request = order.request
        subscription = order.subscription

        with atomic():
            services = [
                BasketService(client),
                RequestService(client),
                SubscriptionService(client),
            ]

            # 1. we are creating invoices for every service we are offering to client
            for item in services:
                item.create_invoice(
                    order=order, basket=basket, request=request, subscription=subscription
                )

            order.refresh_from_db()
            invoice_list = order.invoice_list.all()

            # 2. we are calculating discount for client before charging
            # and persisting them in db
            if coupon:
                self._calculate_and_apply_discount(coupon, invoice_list)

            # 3. we are charging client for every service and invoices of them
            for item in services:
                item.charge(order=order, basket=basket, request=request, subscription=subscription)

            # 4. we are calling last hooks
            for item in services:
                item.checkout(
                    order=order, basket=basket, request=request, subscription=subscription
                )

        self._order = order

        return self.get_container()

    def prepare(self, request: Request) -> Order:
        """
        Method prepares Order entity to be ready.
        After this method, we can add items to basket in POS.
        """

        client = self._client

        with atomic():
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

    def finalize(self, order: Order) -> Order:
        """
        Last method in payment flow, that marks order as paid and
        calls success events.
        """

        self._order = order
        order_id = order.id

        with atomic():
            order.payment = PaymentChoices.PAID

            if order.is_save_card:
                order.card = self._client.main_card
                order.save()

        self._notify_client_on_new_order()
        generate_pdf_from_html.send(
            order_id=order_id,
        )

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

    def _calculate_and_apply_discount(self, coupon: Coupon, invoice_list: List[Invoice]):
        for invoice in invoice_list:
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
