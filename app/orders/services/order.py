from django.db.transaction import atomic

from billing.choices import Purpose
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
    """

    def __init__(self, client: Client):
        self._client = client

    def checkout(self, basket: Basket, delivery: Delivery):
        client = self._client
        subscription = client.subscription
        invoice_service = InvoiceService(client)
        delivery_discount_service = DeliveryDiscountService(client, subscription)

        with atomic():
            total_amount = sum([basket.amount, delivery.amount])
            total_discount = sum([basket.discount, delivery.discount])

            invoice = invoice_service.get_or_create(
                amount=total_amount, discount=total_discount, purpose=Purpose.ORDER,
            )

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
