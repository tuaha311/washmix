from typing import Optional, Tuple

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
from subscriptions.models import Subscription
from subscriptions.services.subscription import SubscriptionService
from subscriptions.utils import is_advantage_program
from users.models import Client, Employee


class OrderService:
    """
    This service is responsible for TOTAL handling of order:
        - Basket info
        - Subscription info
        - Delivery info
    """

    def __init__(self, client: Client, order: Order = None):
        self._client = client
        self._order = order

    def checkout(self, order: Order) -> Tuple[OrderContainer, bool]:
        """
        Method to charge total invoice of order.

        At the checkout stage we are:
            - Refreshing and flushing total amount and discount for every entity (Subscription, Basket, Request)
            - Aggregating amounts and discounts into single invoice
            - Applying coupons (if the are exists)
            - Calling confirming hooks on services
            - Charging client
            - Firing final hooks
        """

        coupon = order.coupon
        client = self._client
        basket = order.basket
        request = order.request
        subscription = order.subscription

        service_list = [
            BasketService(client),
            RequestService(client),
            SubscriptionService(client),
        ]

        with atomic():
            # 1. aggregate into invoice
            invoice = self._create_and_attach_aggregated_invoice(
                order=order,
                basket=basket,
                request=request,
                subscription=subscription,
                service_list=service_list,
            )

            # 2. we are calculating discount for client before charging
            # and persisting them in db
            if coupon:
                self._calculate_and_apply_discount(coupon, invoice)

            # 3. we are trying to confirm some corner cases
            for item in service_list:
                item.confirm(
                    order=order,
                    basket=basket,
                    request=request,
                    subscription=subscription,
                    invoice=invoice,
                )

            # 4. charge for invoice
            payment_service = PaymentService(client, invoice)
            payment_service.charge()

            # 5. we are calling last hooks
            for item in service_list:
                item.checkout(
                    order=order, basket=basket, request=request, subscription=subscription
                )

            # 6. let's save a client's current subscription that used on this order
            order.discount_by_subscription = client.subscription
            order.save()

        self._order = order
        charge_successful = payment_service.charge_successful

        return self.get_container(), charge_successful

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

        self._notify_admin_list_on_new_order()

        return order

    def get_order_by_request(self, request: Request) -> Optional[Order]:
        """
        Try to find order by client and request.
        """

        client = self._client
        order = None

        try:
            order = Order.objects.get(client=client, request=request)
        except Order.DoesNotExist:
            pass

        return order

    def is_formed(self, order: Order) -> bool:
        """
        Method that checks order for different indicators to show it was already formed or not:
            - If order found
            - If Order has invoice
        """

        formed = False

        if order and order.invoice:
            formed = True

        return formed

    def fail(self, order: Order):
        """
        Method that handles Stripe Fail Webhook call.
        """

        order.payment = OrderPaymentChoices.FAIL
        order.save()

        self._order = order

        self._notify_client_on_payment_fail()
        self._notify_admin_on_payment_fail()

    def _create_and_attach_aggregated_invoice(
        self,
        order: Order,
        basket: Basket,
        request: Request,
        subscription: Subscription,
        service_list: list,
    ) -> Invoice:
        """
        We are calculating total amount and discount for every entity and grouping them into
        single Invoice.
        """

        client = self._client
        purpose = InvoicePurpose.SUBSCRIPTION if subscription else InvoicePurpose.ORDER
        raw_entity_list = [basket, request, subscription]
        entity_list = [item for item in raw_entity_list if item]

        # 1. we are refreshing and flushing to DB total amount and discount for
        # every paid entity and corresponding service
        for item in service_list:
            item.refresh_amount_with_discount(
                order=order, basket=basket, request=request, subscription=subscription
            )

        amount = sum([item.amount for item in entity_list])
        discount = sum([item.discount for item in entity_list])

        invoice = Invoice.objects.create(
            client=client,
            amount=amount,
            discount=discount,
            purpose=purpose,
        )
        order.invoice = invoice
        order.save()

        return invoice

    def _calculate_and_apply_discount(self, coupon: Coupon, invoice: Invoice):
        amount = invoice.amount

        coupon_service = CouponService(amount, coupon)

        invoice.discount = coupon_service.apply_coupon()
        invoice.save()

    def _notify_admin_list_on_new_order(self):
        client_id = self._client.id
        order_id = self._order.id
        subscription = self._client.subscription
        is_advantage = is_advantage_program(subscription.name)
        recipient_list = settings.ADMIN_EMAIL_LIST

        send_email.send(
            event=settings.NEW_ORDER,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
                "order_id": order_id,
                "is_advantage": is_advantage,
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
