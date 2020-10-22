from django.db import models


class CommonDeliveries(models.Model):
    # usual fields
    comment = models.TextField(
        verbose_name="comment",
        blank=True,
    )
    is_rush = models.BooleanField(
        verbose_name="is a rush / urgent delivery",
        default=False,
    )

    class Meta:
        abstract = True
