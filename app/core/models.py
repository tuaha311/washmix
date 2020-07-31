from django.conf import settings
from django.db import models

from core.common_models import Common
from orders.models import Order


class Phone(Common):
    """
    Phone number of our clients.
    """

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


class City(Common):
    """
    City that we support.
    Only at this cities we can pickup or deliver.
    """

    name = models.CharField(
        verbose_name="name",
        max_length=50,
    )

    class Meta:
        verbose_name = "city"
        verbose_name_plural = "cities"


class ZipCode(Common):
    """
    Zip codes of supported addresses where our laundry works.
    Only at this zip codes we can pickup or deliver.
    """

    city = models.ForeignKey(
        "core.City",
        related_name="zipcode_list",
        on_delete=models.CASCADE,
    )

    value = models.CharField(
        verbose_name="value",
        max_length=20,
    )

    class Meta:
        verbose_name = "zip code"
        verbose_name_plural = "zip codes"


class Address(Common):
    """
    Addresses of our clients.
    """

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
    """
    Subscription plans (also called "Packages") that we offer to clients.
    At the moment of 31/07/2020 we have 3 packages:
    - PAYC (Pay As You Clean)
    - GOLD
    - PLATINUM
    """

    PAYC = "payc"
    GOLD = "gold"
    PLATINUM = "platinum"
    NAME_MAP = {
        PAYC: "PAYC",
        GOLD: "GOLD",
        PLATINUM: "PLATINUM",
    }
    NAME_CHOICES = list(NAME_MAP.items())

    name = models.CharField(
        verbose_name="name",
        choices=NAME_CHOICES,
        unique=True,
    )
    price = models.FloatField(
        verbose_name="price",
    )
    dry_clean = models.IntegerField(
        verbose_name="discount on dry clean + press",
    )
    laundry = models.IntegerField(
        verbose_name="discount on laundry + press",
    )
    wash_fold = models.IntegerField(
        verbose_name="discount on wash & fold",
    )
    has_delivery = models.BooleanField(
        verbose_name="has a free delivery",
    )
    has_welcome_box = models.BooleanField(
        verbose_name="has a welcome box",
    )
    has_seasonal_garment = models.BooleanField(
        verbose_name="has a seasonal garment storage",
    )
    has_credit_back = models.BooleanField(
        verbose_name="has a credit back",
    )

    class Meta:
        verbose_name = "package"
        verbose_name_plural = "packages"


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

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"
