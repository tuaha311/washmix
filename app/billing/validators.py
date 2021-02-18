import logging
from typing import Tuple

from django.conf import settings
from django.db.models import ObjectDoesNotExist

import stripe
from rest_framework import serializers
from rest_framework.request import Request

from billing.models import Invoice
from billing.stripe_helper import StripeHelper
from users.models import Client

logger = logging.getLogger(__name__)


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


def validate_stripe_event(
    payment: stripe.PaymentMethod,
    request: Request,
    enable_ip_check: bool = False,
) -> Tuple[bool, dict]:
    errors = {}
    valid = False

    if enable_ip_check:
        ip_address = request.META["HTTP_X_FORWARDED_FOR"]

        # don't allowing other IPs excluding Stripe's IPs
        if ip_address not in settings.STRIPE_WEBHOOK_IP_WHITELIST:
            errors = {
                "reason": "ip_not_in_whitelist",
            }

            logger.info(f"IP address {ip_address} not in whitelist.")

            return valid, errors

    try:
        invoice_id = payment.metadata.invoice_id
        invoice = Invoice.objects.get(pk=invoice_id)
    except ObjectDoesNotExist:
        errors = {
            "reason": "invoice_doesnt_exists",
        }

        logger.info(f"Invoice doesn't exists.")

        return valid, errors

    try:
        stripe_id = payment.customer
        Client.objects.get(stripe_id=stripe_id)
    except ObjectDoesNotExist:
        errors = {
            "reason": "client_doesnt_exists",
        }

        logger.info(f"Client doesn't exists.")

        return valid, errors

    if invoice.is_paid:
        errors = {
            "reason": "invoice_is_paid",
        }

        logger.info(f"{invoice} is already paid.")

        return valid, errors

    valid = True

    return valid, errors
