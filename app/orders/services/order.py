from typing import List

from django.conf import settings
from django.db.transaction import atomic

from billing.choices import Purpose
from billing.models import Coupon, Invoice
from billing.services.coupon import CouponService
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from deliveries.choices import Kind
from deliveries.containers.request import RequestContainer
from deliveries.models import Request
from notifications.tasks import send_email
from orders.choices import PaymentChoices
from orders.containers.basket import BasketContainer
from orders.containers.order import OrderContainer
from orders.models import Basket, Order
from subscriptions.containers import SubscriptionContainer
from subscriptions.models import Subscription
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
        """

        invoice_list = order.invoice_list.all()

        with atomic():
            for invoice in invoice_list:
                self.charge(invoice)

        self._order = order

        return self.get_container()

    def create_basket_invoice(
        self,
        order: Order,
        basket: Basket,
    ) -> List[Invoice]:
        client = self._client
        subscription = client.subscription
        invoice_service = InvoiceService(client)
        basket_container = BasketContainer(subscription, basket)

        basket_invoice = invoice_service.update_or_create(
            order=order,
            amount=basket_container.amount,
            discount=basket_container.discount,
            purpose=Purpose.BASKET,
        )
        basket.invoice = basket_invoice
        basket.save()

        self._order = order

        return [basket_invoice]

    def create_delivery_invoice(
        self,
        order: Order,
        basket: Basket,
        request: Request,
    ) -> List[Invoice]:
        client = self._client
        subscription = client.subscription
        invoice_service = InvoiceService(client)
        basket_container = BasketContainer(subscription, basket)
        request_container = RequestContainer(subscription, request, basket_container)

        # we have 2 kind - Pickup, Dropoff
        # and for every of Delivery we create an invoice
        kind_of_deliveries = Kind.MAP.keys()
        invoice_list = []

        for kind in kind_of_deliveries:
            delivery_container_name = f"{kind}_container"
            delivery_container = getattr(request_container, delivery_container_name)

            delivery_invoice = invoice_service.update_or_create(
                order=order,
                amount=delivery_container.amount,
                discount=delivery_container.discount,
                purpose=kind,
            )

            invoice_attribute_name = f"{kind}_invoice"
            setattr(request, invoice_attribute_name, delivery_invoice)

            invoice_list.append(delivery_invoice)

        request.save()

        self._order = order

        return invoice_list

    def create_subscription_invoice(
        self,
        order: Order,
        subscription: Subscription,
    ) -> List[Invoice]:
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

        self._order = order

        return [subscription_invoice]

    def apply_coupon(self, order: Order, coupon: Coupon) -> OrderContainer:
        invoice_list = order.invoice_list.all()

        order.coupon = coupon
        order.save()

        # when we link Coupon with Order
        # discount calculated dynamically on the fly inside OrderContainer
        self._order = order

        for invoice in invoice_list:
            amount = invoice.amount
            coupon_service = CouponService(amount, coupon)
            invoice.discount = coupon_service.apply_coupon()
            invoice.save()

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
        self._order = order

        with atomic():
            order.payment = PaymentChoices.PAID

            if order.is_save_card:
                order.card = self._client.main_card
                order.save()

        self._notify_client_on_new_order()

        return order

    def fail(self, order: Order):
        order.payment = PaymentChoices.FAIL
        order.save()

        self._notify_client_on_payment_fail()
        self._notify_admin_on_payment_fail()

    def _notify_client_on_new_order(self):
        client_id = self._client.id
        order_id = self._order.id

        send_email.send(
            client_id=client_id,
            event=settings.NEW_ORDER,
            extra_context={
                "order_id": order_id,
            },
        )

    def _notify_client_on_payment_fail(self):
        pass

    def _notify_admin_on_payment_fail(self):
        pass

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
