import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models.code import code_string
from notifications.tasks import send_email
from billing.stripe_helper import StripeHelper
from users.models import Client, Code
from django.contrib.auth.signals import user_logged_in
from django.urls import reverse
from notifications.tasks import send_email

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


def send_otp_via_email_to_super_admin(email, code):
    send_email(
        event=f"Your verification code is: {code}",
        recipient_list=[email]
    )

@receiver(user_logged_in)
def generate_code_for_superadmin(sender, request, user, **kwargs):
    if user.is_superuser:
        existing_code = Code.objects.get(user=user)
        if existing_code:
            code = code_string()
            existing_code.number = code
            existing_code.authenticated = False
            existing_code.save()
            send_otp_via_email_to_super_admin(email=user.email, code=code)
            print(code, "Updated Code")
            
        else:
            # Generate a Code instance for the super admin
            code = Code(user=user)
            code.save()
            send_otp_via_email_to_super_admin(email=user.email, code=code)
            print(code, "Generated Code")