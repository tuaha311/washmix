import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from billing.stripe_helper import StripeHelper
from locations.models import Address

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=Address, dispatch_uid="update_address_stripe_info")
def update_address_stripe_info(
    instance: Address, created: bool, raw: bool, update_fields: frozenset, **kwargs
):
    """
    Signal handler for Address that updates Stripe's Customer info.
    """

    # We are ignoring raw signals
    # Ref - https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
    if raw:
        logger.info("Raw signal call - ignoring")
        return None

    address = instance
    client = address.client
    main_address = client.main_address
    stripe_id = client.stripe_id
    stripe_helper = StripeHelper(client)

    if main_address and client.main_address != address:
        logger.info("Not a main address")
        return None

    if not stripe_id:
        logger.info(f"Client {client.email} doesn't have an Stripe ID.")
        return None

    if not update_fields:
        logger.info("No update fields")
        return None

    if settings.UPDATE_FIELDS_FOR_ADDRESS & update_fields:
        address = {
            "line1": address.address_line_1,
            "line2": address.address_line_2,
            "postal_code": address.zip_code.value,
            "country": settings.DEFAULT_COUNTRY,
        }
        stripe_helper.update_customer_info(stripe_id, address=address)

        logger.info(f"Updating address info for {client.email}")
