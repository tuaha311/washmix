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


def validate_stripe_event():
    if self.enable_ip_check:
        ip_address = self._request.META["HTTP_X_FORWARDED_FOR"]

        # don't allowing other IPs excluding Stripe's IPs
        if ip_address not in settings.STRIPE_WEBHOOK_IP_WHITELIST:
            self.body = {
                "reason": "ip_not_in_whitelist",
            }
            self.status = self.error_status

            logger.info(f"IP address {ip_address} not in whitelist.")

            return False

    try:
        invoice = self.invoice
    except ObjectDoesNotExist:
        self.body = {
            "reason": "invoice_doesnt_exists",
        }
        self.status = self.error_status

        logger.info(f"Invoice doesn't exists.")

        return False

    if invoice.is_paid:
        self.body = {
            "reason": "invoice_is_paid",
        }
        self.status = self.error_status

        logger.info(f"{invoice} is already paid.")

        return False

    return True
