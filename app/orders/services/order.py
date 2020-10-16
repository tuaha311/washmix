from django.db.transaction import atomic

from billing.models import Invoice
from billing.services.invoice import InvoiceService
from billing.services.payments import PaymentService
from deliveries.models import Delivery
from orders.models import Basket, Order
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

    def checkout(self, basket: Basket):
        invoice_service = InvoiceService(self._client)
        delivery = self._delivery

        with atomic():
            total_amount = sum([basket.amount, delivery.amount])
            invoice = invoice_service.get_or_create(total_amount, Invoice.ORDER)

            order = Order.objects.create(
                client=self._client, delivery=delivery, invoice=invoice, basket=basket,
            )

        return order, invoice

    def charge(self, invoice: Invoice):
        """
        We are charging user for:
        - basket amount
        - delivery amount
        - extras amount
        """

        payment_service = PaymentService(self._client, invoice)
        payment_service.charge()

    def process(self):
        pass
