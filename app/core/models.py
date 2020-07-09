from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from rest_framework_expiring_authtoken.models import ExpiringToken

from modules.enums import CouponType
from orders.models import Order


class PickupAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pickupaddress")
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(default="")
    state = models.CharField(max_length=30, default="")
    city = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=30)
    title = models.CharField(max_length=80, default="")

    added_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)


class DropoffAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dropoffaddress")
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(default="")
    state = models.CharField(max_length=30, default="")
    city = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=30)
    title = models.CharField(max_length=80, default="")

    added_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)


class PackageType(models.Model):
    package_name = models.TextField(default="")
    package_price = models.FloatField(default=0)


class Coupons(models.Model):
    name = models.CharField(max_length=30)
    amount_off = models.FloatField(default=0)
    percentage_off = models.FloatField(default=0)
    start_date = models.DateTimeField(default=timezone.now())
    valid = models.BooleanField(default=True)
    max_redemptions = models.IntegerField(default=1)
    coupon_type = models.CharField(
        max_length=30,
        choices=[(item, item.value) for item in CouponType],
        null=True,
        default=CouponType.FIRST.value,
    )

    added_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    def apply_coupon(self, total_amount):
        return (self.percentage_off * total_amount) / 100


class Product(models.Model):
    name = models.CharField(max_length=50)
    product = models.ForeignKey(
        "self", null=True, related_name="children", on_delete=models.CASCADE
    )
    price = models.FloatField(default=0)


# class Balance(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     current_balance = models.FloatField(null=False)
#     added_datetime = models.DateTimeField(auto_now_add=True)
#     updated_datetime = models.DateTimeField(auto_now=True)
#
# class UserPurchases(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     type = models.CharField(max_length=100, null=False)
#     value = models.CharField(max_length=100, null=False)
#     cost = models.FloatField(null=False)
#     added_datetime = models.DateTimeField(auto_now_add=True)
#     updated_datetime = models.DateTimeField(auto_now=True)
