from django.db import models

from core.common_models import Common
from core.validators import validate_phone
from orders.models import Order


class Phone(Common):
    """
    Client-side entity.

    Phone number of our clients.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        related_name="phone_list",
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        verbose_name="title of phone",
        max_length=80,
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

    def __str__(self):
        return self.number
