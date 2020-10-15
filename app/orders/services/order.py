from django.db.transaction import atomic

from billing.models import Invoice
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from deliveries.models import Delivery
from orders.models import Order
from orders.services.basket import BasketService
from orders.services.extras import ExtrasService
from users.models import Client


class OrderService:
    """
    This service is responsible for TOTAL handling of order:
        - Basket info
        - Delivery info
        - Extras info
    """

    def __init__(self, client: Client, delivery: Delivery):
        self._client = client
        self._delivery = delivery
        self._extras_service = ExtrasService(client)
        self._basket_service = BasketService(self._client)

    def charge(self, invoice: Invoice):
        """
        We are charging user for:
        - basket amount
        - delivery amount
        - extras amount
        """

        payment_service = PaymentService(self._client, invoice)
        payment = payment_service.charge()

        return payment

    def checkout(self):
        invoice_service = InvoiceService(self._client)
        basket = self.basket
        delivery = self._delivery

        with atomic():
            total_amount = sum([basket.amount, delivery.amount])
            invoice = invoice_service.get_or_create(total_amount)

            order = Order.objects.create(
                client=self._client, delivery=delivery, invoice=invoice, basket=basket,
            )

        return order

    @property
    def basket(self):
        return self._basket_service.basket

    def process(self):
        pass

    @property
    def delivery(self):
        pass

    @property
    def extras(self):
        pass
