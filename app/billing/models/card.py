from django.db import models

from core.behaviors import Stripeable
from core.common_models import Common


class Card(Stripeable, Common):
    """
    Client-side entity.

    Credit or debit card.
    We doesn't store anything related to card credentials - only Stripe ID.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="card_list",
    )

    last = models.CharField(
        verbose_name="last 4 digits",
        max_length=4,
    )
    expiration_month = models.PositiveSmallIntegerField(
        verbose_name="expiration month",
    )
    expiration_year = models.PositiveSmallIntegerField(
        verbose_name="expiration year",
    )
    is_active = models.BooleanField(
        verbose_name="card is active",
        default=True,
    )

    class Meta:
        verbose_name = "card"
        verbose_name_plural = "cards"

    def __str__(self):
        return f"*** {self.last} - {self.expiration_month}/{self.expiration_year}"
