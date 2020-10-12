from rest_framework import serializers

from billing.stripe_helper import StripeHelper
from users.models import Client


def validate_payment_method(client: Client):
    """
    Use this validator at start of checkout process.
    """

    stripe_helper = StripeHelper(client)

    if not stripe_helper.payment_method_list:
        raise serializers.ValidationError(
            detail="You have no active payment methods.", code="no_payment_methods",
        )
