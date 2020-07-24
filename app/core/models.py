from django.conf import settings
from django.db import models

from core.common_models import Common
from orders.models import Order


class Phone(Common):
    number = models.CharField(
        verbose_name="number",
        max_length=20,
    )

    class Meta:
        verbose_name = "phone"
        verbose_name_plural = "phones"


class ZipCode(Common):
    value = models.CharField(
        verbose_name="value",
        max_length=20,
    )


class Address(Common):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="address_list")

    address_line_1 = models.TextField()
    address_line_2 = models.TextField(default="")
    state = models.CharField(max_length=30, default="")
    city = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=30)
    title = models.CharField(max_length=80, default="")


class Package(Common):
    name = models.TextField(default="")
    price = models.FloatField(default=0)


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
