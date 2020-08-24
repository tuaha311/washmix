from django.db import models


class Stripeable(models.Model):
    """
    Behavior for model that define default fields
    for Stripe integration.
    """

    stripe_id = models.CharField(verbose_name="Stripe ID", max_length=100, blank=True, unique=True,)

    class Meta:
        abstract = True
