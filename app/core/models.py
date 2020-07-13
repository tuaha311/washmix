from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import localtime

from core.common_models import Common
from modules.enums import CouponType
from orders.models import Order


class Address(Common):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="address_list")

    address_line_1 = models.TextField()
    address_line_2 = models.TextField(default="")
    state = models.CharField(max_length=30, default="")
    city = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=30)
    title = models.CharField(max_length=80, default="")


class Package(Common):
    name = models.TextField(default="")
    price = models.FloatField(default=0)


class Coupon(Common):
    name = models.CharField(max_length=30)
    amount_off = models.FloatField(default=0)
    percentage_off = models.FloatField(default=0)
    start_date = models.DateTimeField(default=localtime)
    valid = models.BooleanField(default=True)
    max_redemptions = models.IntegerField(default=1)
    coupon_type = models.CharField(
        max_length=30,
        choices=[(item, item.value) for item in CouponType],
        null=True,
        default=CouponType.FIRST.value,
    )

    def apply_coupon(self, total_amount):
        return (self.percentage_off * total_amount) / 100


class Product(Common):
    product = models.ForeignKey(
        "self", null=True, related_name="children", on_delete=models.CASCADE
    )

    name = models.CharField(max_length=50)
    price = models.FloatField(default=0)


class Notification(Common):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_list"
    )

    message = models.TextField(default="")
