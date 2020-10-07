from django.conf import settings
from django.db import models

from core.common_models import Common
from subscriptions.common_models import CommonPackageSubscription


class Package(CommonPackageSubscription, Common):
    """
    NOTE: Package / Subscription uses the same pattern such Schedule / Delivery.

    Main Packages that we offer to clients.
    It is a templates that we use to create concrete instances of
    Packages called Subscription.
    This approach need to us because we should store historical price
    and package conditions per user.

    At the moment of 31/07/2020 we have 3 packages:
    - PAYC (Pay As You Clean)
    - GOLD
    - PLATINUM
    """

    name = models.CharField(
        verbose_name="name",
        max_length=20,
        choices=settings.PACKAGE_NAME_CHOICES,
        unique=True,
    )
    description = models.CharField(
        verbose_name="description of package",
        max_length=100,
        blank=True,
    )

    class Meta:
        verbose_name = "package"
        verbose_name_plural = "packages"

    def __str__(self):
        return f"{self.get_name_display()} - {self.dollar_price} $"
