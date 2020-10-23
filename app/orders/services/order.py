from typing import List, Tuple

from django.db.transaction import atomic

from billing.choices import Purpose
from billing.models import Invoice
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from deliveries.choices import Kind
from deliveries.containers import RequestContainer
from deliveries.models import Request
from orders.choices import Status
from orders.containers.basket import BasketContainer
from orders.containers.order import OrderContainer
from orders.models import Basket, Order
from users.models import Client


class OrderService:
    """
    This service is responsible for TOTAL handling of order:
        - Basket info
        - Delivery info
    """

    def __init__(self, client: Client):
        self._client = client
        self._order = None

    def checkout(self, basket: Basket, request: Request) -> Tuple[Order, List[Invoice]]:
        client = self._client
        subscription = client.subscription
        invoice_service = InvoiceService(client)
        basket_container = BasketContainer(subscription, basket)
        request_container = RequestContainer(subscription, request, basket_container)

        with atomic():
            basket_invoices = self._create_basket_invoice(
                basket=basket, basket_container=basket_container, invoice_service=invoice_service,
            )
            delivery_invoices = self._create_delivery_invoice(
                request=request,
                request_container=request_container,
                invoice_service=invoice_service,
            )

            invoice_list = [*basket_invoices, *delivery_invoices]

            order = Order.objects.create(
                client=self._client, request=request, basket=basket, status=Status.ACCEPTED,
            )
            order.invoice_list.set(invoice_list)

        self._order = order

        return order, invoice_list

    def charge(self, invoice: Invoice):
        """
        We are charging user for:
        - basket amount
        - pickup delivery amount
        - dropoff delivery amount
        """

        payment_service = PaymentService(self._client, invoice)
        payment_service.charge()

    @property
    def container(self):
        order = self._order

        assert order, "Call .checkout before accessing to .container property"

        container = OrderContainer(order)

        return container

    def _create_basket_invoice(
        self, basket: Basket, basket_container: BasketContainer, invoice_service: InvoiceService
    ) -> List[Invoice]:
        invoice_list = []

        basket_invoice = invoice_service.create(
            amount=basket_container.amount,
            discount=basket_container.discount,
            purpose=Purpose.BASKET,
        )
        basket.invoice = basket_invoice
        basket.save()

        invoice_list.append(basket_invoice)

        return invoice_list

    def _create_delivery_invoice(
        self, request: Request, request_container: RequestContainer, invoice_service: InvoiceService
    ) -> List[Invoice]:
        # we have 2 kind - Pickup, Dropoff
        # and for every of Delivery we create an invoice
        kind_of_deliveries = Kind.MAP.keys()
        invoice_list = []

        for kind in kind_of_deliveries:
            delivery_invoice = invoice_service.create(
                amount=request_container.amount,
                discount=request_container.discount,
                purpose=Purpose.DELIVERY,
            )
            invoice_attribute_name = f"{kind}_invoice"
            setattr(request, invoice_attribute_name, delivery_invoice)

            invoice_list.append(delivery_invoice)

        request.save()

        return invoice_list

    def process(self):
        pass
