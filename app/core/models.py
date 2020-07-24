from django.conf import settings
from django.db import models

from core.common_models import Common
from orders.models import Order


class Phone(Common):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="user",
        related_name="phone_list",
        on_delete=models.CASCADE,
    )

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

    class Meta:
        verbose_name = "zip code"
        verbose_name_plural = "zip codes"


class Address(Common):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="user",
        related_name="address_list",
        on_delete=models.CASCADE,
    )
    zip_code = models.ForeignKey(
        "core.ZipCode",
        verbose_name="zip code",
        related_name="address_list",
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        verbose_name="title of address",
        max_length=80,
    )
    address_line_1 = models.TextField(
        verbose_name="address line 1",
    )
    address_line_2 = models.TextField(
        verbose_name="address line 2",
    )
    state = models.CharField(
        verbose_name="state",
        max_length=30,
    )
    city = models.CharField(
        verbose_name="city",
        max_length=30,
    )

    class Meta:
        verbose_name = "address"
        verbose_name_plural = "addresses"


class Package(Common):
    name = models.TextField(
        verbose_name="name",
    )
    price = models.FloatField(
        verbose_name="price",
    )


class Product(Common):
    product = models.ForeignKey(
        "self",
        null=True,
        related_name="children",
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        verbose_name="name",
        max_length=50,
    )
    price = models.FloatField(
        verbose_name="price",
    )


class Notification(Common):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="user",
        related_name="notification_list",
        on_delete=models.CASCADE,
    )

    message = models.TextField(
        verbose_name="message",
    )
