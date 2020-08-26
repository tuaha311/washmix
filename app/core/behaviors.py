from django.conf import settings
from django.db import models


class Stripeable(models.Model):
    """
    Behavior for model that define default fields
    for Stripe integration.
    """

    stripe_id = models.CharField(
        verbose_name="Stripe ID", max_length=100, blank=True, null=True, unique=True,
    )

    class Meta:
        abstract = True


class Amountable(models.Model):
    """
    Behavior that defines amount field in cents.
    Also, it provides .dollar_amount property
    """

    amount = models.BigIntegerField(verbose_name="amount in cents",)

    class Meta:
        abstract = True

    @property
    def dollar_amount(self):
        return self.amount / settings.CENTS_IN_DOLLAR
