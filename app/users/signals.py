import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from notifications.tasks import send_email
from billing.stripe_helper import StripeHelper
from users.models import Client

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=Client, dispatch_uid="update_client_stripe_info")
def update_client_stripe_info(
    instance: Client, created: bool, raw: bool, update_fields: frozenset, **kwargs
):
    """
    Signal handler for Client that updates Stripe's Customer info:
        - Phone
        - Address
    """

    # We are ignoring raw signals
    # Ref - https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
    if raw:
        logger.info("Raw signal call - ignoring")
        return None

    if not update_fields:
        logger.info("No update fields")
        return None

    client = instance
    main_phone = client.main_phone
    stripe_id = client.stripe_id
    billing_address = client.billing_address
    stripe_helper = StripeHelper(client)

    if not stripe_id:
        logger.info(f"Client {client.email} doesn't have an Stripe ID.")
        return None

    if "main_phone" in update_fields and main_phone:
        phone = main_phone.number
        stripe_helper.update_customer_info(stripe_id, phone=phone)

        logger.info(f"Updating phone info for {client.email}")

    if "billing_address" in update_fields and billing_address:
        address = {
            "line1": billing_address.get("address_line_1", ""),
            "line2": billing_address.get("address_line_2", ""),
            "postal_code": billing_address.get("zip_code", ""),
            "country": settings.DEFAULT_COUNTRY,
        }
        stripe_helper.update_customer_info(stripe_id, address=address)

        logger.info(f"Updating billing address info for {client.email}")


@receiver(post_save, sender=User, dispatch_uid="update_user_stripe_info")
def update_user_stripe_info(
    instance: User, created: bool, raw: bool, update_fields: frozenset, **kwargs
):
    """
    Signal handler for User that updates Stripe's Customer info:
        - Full Name
    """

    # We are ignoring raw signals
    # Ref - https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
    if raw:
        logger.info("Raw signal call - ignoring")
        return None

    if not update_fields:
        logger.info("No update fields")
        return None

    try:
        user = instance
        client = user.client
    except ObjectDoesNotExist:
        return None

    stripe_id = client.stripe_id
    stripe_helper = StripeHelper(client)

    if settings.UPDATE_FIELDS_FOR_USER & update_fields:
        full_name = client.full_name
        stripe_helper.update_customer_info(stripe_id, name=full_name)

        logger.info(f"Updating name info for {client.email}")

@receiver(post_delete, sender=Client)
def client_post_delete(sender, instance, **kwargs):
    client = instance

    # Perform actions after the object has been deleted
    # For example, you can log the deletion or trigger other processes
    recipient_list = [*settings.ADMIN_EMAIL_LIST, client.email]

    send_email.send(
        event=settings.ACCOUNT_REMOVED,
        recipient_list=recipient_list,
        extra_context={
            "full_name": client.full_name,
        },
    )
