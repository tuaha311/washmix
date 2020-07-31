from django.db import models

from core.common_models import Common


class Card(Common):
    """
    Credit or debit card.
    We doesn't store anything related to card credentials - only Stripe ID.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="card_list",
    )

    stripe_card_id = models.TextField(
        verbose_name="Stripe card ID",
    )
    is_active = models.BooleanField(
        verbose_name="card is active",
        default=False,
    )

    class Meta:
        verbose_name = "card"
        verbose_name_plural = "cards"
