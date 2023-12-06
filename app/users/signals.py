from django.contrib.auth.models import Group
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models.employee import Employee
from users.models.code import code_string
from notifications.tasks import send_email, send_sms
from billing.stripe_helper import StripeHelper
from users.models import Client, Code
from django.contrib.auth.signals import user_logged_in
from django.urls import reverse
from notifications.tasks import send_email
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

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


def send_otp_via_email_to_super_admin(request, email, code, phone=None):
    try:
        if phone:
            send_sms.send_with_options(
            kwargs={
                "event": settings.ADMIN_LOGIN_OTP,
                "recipient_list": [phone],
                "extra_context": {
                    "code": code,
                },
            },
            delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
            )
            messages.success(request, f'A verification code has been sent to your phone number "{phone}"')
        else:
            print("Email message requested")
            send_email.send(
                event=settings.SUPER_ADMIN_OTP,
                recipient_list=[email],
                extra_context={
                    "email": email,
                    "code": code,
                },
            )
            messages.success(request, f'A verification code has been sent to your email "{email}"')
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")

@receiver(user_logged_in)
def generate_code_for_superadmin(sender, request, user, **kwargs):
    groups = user.groups.all()
    user_is_admin = any("admin" in group.name.lower() for group in groups)

    try:
        employee_user = Employee.objects.get(user=user)
        phone = employee_user.phone if employee_user.phone else None
    except ObjectDoesNotExist:
        # Handle the case when no Employee object is found for the user
        phone = None  # or provide a default value or log a message

    if user_is_admin or user.is_superuser:
        try:
            existing_code = Code.objects.get(user=user)
            code = code_string()
            existing_code.number = code
            existing_code.authenticated = False
            existing_code.save()
            send_otp_via_email_to_super_admin(request, email=user.email, code=code, phone=phone)

        except Code.DoesNotExist:
            # Generate a Code instance for the super admin
            code = Code(user=user)
            code.save()
            send_otp_via_email_to_super_admin(request, email=user.email, code=code.number, phone=phone)

