from django.conf import settings
from django.db import models

import phonenumbers

from core.common_models import Common
from core.validators import validate_phone
from orders.models import Order


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
        unique=True,
        validators=[validate_phone],
    )

    class Meta:
        verbose_name = "phone"
        verbose_name_plural = "phones"

    @classmethod
    def format_number(cls, value):
        phone = phonenumbers.parse(value, settings.DEFAULT_PHONE_REGION)
        return phonenumbers.format_number(phone, settings.DEFAULT_PHONE_FORMAT)


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
