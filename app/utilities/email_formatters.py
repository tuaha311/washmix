from datetime import datetime

from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from api.legacy.permissions import account_activation_token
from modules.constant import WASHMIX_TEAM_ORDER_DROPOFF, WASHMIX_TEAM_ORDER_PICK


def format_user(**kwargs):
    """Perform any additional content formatting steps here"""

    user = kwargs.get("user")

    def email_formatter():
        # user.is_active = False
        # user.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = account_activation_token.make_token(user)

        message = {
            "to": [{"email": user.email or user.username}],
            "template_id": "d-3dca30fda91a41fd9d283b4841982d14",
            "email_data": {
                "uid": uid,
                "token": token,
                "url": settings.USER_ACTIVATION_URL.format(**{"uid": uid, "token": token}),
                "protocol": "https",
                "site_name": "washmix",
                "domain": "example.com",
                "email": user.email or user.email,
            },
        }
        return message

    return email_formatter


def format_order(**kwargs):
    user = kwargs.get("user")
    address = kwargs.get("pickup_address")
    pick_from = kwargs.get("pick_from")
    pick_to = kwargs.get("pick_to")

    def order_placement_formatter():
        return {
            "to": [{"email": user.email, "name": user.username}],
            "template_id": "d-c7f0068261504cdfbd89220b0c16ac65",
            "email_data": {
                "from_date": pick_from.strftime("%A %m/%d"),
                "from_hour": pick_from.strftime("%l %p"),
                "to_hour": pick_to.strftime("%l %p"),
                "pickup_address": address.address_line_1,
                "email": user.email,
            },
        }

    return order_placement_formatter


def format_purchase(**kwargs):
    """
    Email formatter to be used when user purchase a package.
    Expects a card, user and a package_name.
    :param kwargs:
    :return:
    """
    users = kwargs.get("users")
    charge = kwargs.get("charge")
    package_name = kwargs.get("package_name")

    source = charge.source
    purchase_date = datetime.now().strftime("%d/%m/%y")

    def email_formatter():
        to = []
        for user in users:
            to.append({"email": user.email, "name": user.username})

        return {
            "to": to,
            "template_id": "d-180c40861e2049ff983ffaecca4eda49",
            "email_data": {
                "amount_paid": float(charge.amount / 100),
                "date": purchase_date,
                "package_name": package_name,
                "receipt_number": charge.receipt_number,
                "payment_method": "%s - %s" % (source.brand, source.last4),
                "email": user.email,
            },
        }

    return email_formatter


def format_order_pickup(**kwargs):
    order = kwargs.get("order")
    user = kwargs.get("user")

    def message_formatter():
        return WASHMIX_TEAM_ORDER_PICK.format(
            user.first_name,
            user.profile.phone,
            order.pickup_address.address_line_1,
            "%s @ %s"
            % (
                order.pick_up_from_datetime.strftime("%A %m/%d"),
                order.pick_up_from_datetime.strftime("%l:%M %p"),
            ),
        )

    return message_formatter


def format_order_dropoff(**kwargs):
    order = kwargs.get("order")
    user = kwargs.get("user")

    def message_formatter():
        return WASHMIX_TEAM_ORDER_DROPOFF.format(
            user.first_name,
            user.profile.phone,
            order.dropoff_address.address_line_1,
            "%s @ %s"
            % (
                order.drop_off_from_datetime.strftime("%A %m/%d"),
                order.drop_off_from_datetime.strftime("%l:%M %p"),
            ),
        )

    return message_formatter
