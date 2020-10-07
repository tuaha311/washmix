from django.db import models

from core.behaviors import Priceable


class CommonPackageSubscription(Priceable, models.Model):
    dry_clean = models.IntegerField(
        verbose_name="discount on dry clean + press",
    )
    laundry = models.IntegerField(
        verbose_name="discount on laundry + press",
    )
    alterations = models.IntegerField(
        verbose_name="alterations discount",
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
    is_most_popular = models.BooleanField(
        verbose_name="most popular badge",
        default=False,
    )

    class Meta:
        abstract = True
