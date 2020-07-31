from django.db import models

from core.common_models import Common
from orders.models import Order


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
        max_length=20,
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


class Phone(Common):
    """
    Phone number of our clients.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
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
