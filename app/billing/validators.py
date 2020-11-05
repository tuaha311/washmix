from rest_framework import serializers

from billing.stripe_helper import StripeHelper


def validate_saved_cards(instance):
    client = instance.client

    if client.card_list.count() == 0:
        raise serializers.ValidationError(
            detail="You have no active card.",
            code="no_card",
        )


def validate_client_can_pay(instance):
    client = instance.client

    stripe_helper = StripeHelper(client)

    if not stripe_helper.payment_method_list:
        raise serializers.ValidationError(
            detail="You have no active payment methods.",
            code="no_payment_methods",
        )


def validate_paid_invoice(instance):
    if instance.is_paid:
        raise serializers.ValidationError(
            detail="You already paid this invoice.",
            code="invoice_already_paid",
        )
