from rest_framework import serializers

from billing.models import Invoice
from billing.stripe_helper import StripeHelper
from orders.models import Order
from users.models import Client


def validate_saved_cards(order: Order):
    client = order.client

    if client.card_list.count() == 0:
        raise serializers.ValidationError(
            detail="You have no active card.", code="no_card",
        )


def validate_client_can_pay(order: Order):
    client = order.client

    stripe_helper = StripeHelper(client)

    if not stripe_helper.payment_method_list:
        raise serializers.ValidationError(
            detail="You have no active payment methods.", code="no_payment_methods",
        )


def validate_paid_invoice(invoice: Invoice):
    if invoice.is_paid:
        raise serializers.ValidationError(
            detail="You already paid this invoice.", code="invoice_already_paid",
        )
