import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from billing.stripe_helper import StripeHelper
from core.models import Phone

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=Phone, dispatch_uid="update_phone_stripe_info")
def update_phone_stripe_info(
    instance: Phone, created: bool, raw: bool, update_fields: frozenset, **kwargs
):
    """
    Signal handler for Phone that updates Stripe's Customer info:
        - Phone
        - Address
    """

    # We are ignoring raw signals
    # Ref - https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
    if raw:
        logger.info("Raw signal call - ignoring")
        return None

    phone = instance
    client = phone.client
    stripe_id = client.stripe_id
    main_phone = client.main_phone
    stripe_helper = StripeHelper(client)

    if main_phone and main_phone != phone:
        logger.info("Not a main phone")
        return None

    if not stripe_id:
        logger.info(f"Client {client.email} doesn't have an Stripe ID.")
        return None

    if not update_fields:
        logger.info("No update fields")
        return None

    if "number" in update_fields:
        number = phone.number
        stripe_helper.update_customer_info(stripe_id, phone=number)

        logger.info(f"Updating phone info for {client.email}")
