from django.conf import settings
from django.db import models

from core.common_models import Common
from core.utils import clone_from_to
from subscriptions.common_models import CommonPackageSubscription


class SubscriptionManager(models.Manager):
    exclude_fields = ["id", "created", "changed",]

    def fill_subscription(self, package, subscription):
        clone_from_to(package, subscription, self.exclude_fields)

        return subscription


class Subscription(CommonPackageSubscription, Common):
    """
    NOTE: Package / Subscription uses the same pattern such Schedule / Delivery.

    Concrete instance of Package.
    It holds all the field of Package, and can be interpreted as
    per user conditions of Package.
    """

    # TODO возможно, стоит сюда перенести связь client
    name = models.CharField(
        verbose_name="name",
        max_length=20,
        choices=settings.PACKAGE_NAME_CHOICES,
    )
    invoice = models.OneToOneField(
        "billing.Invoice",
        verbose_name="invoice",
        related_name="subscription",
        on_delete=models.PROTECT,
    )

    objects = SubscriptionManager()

    class Meta:
        verbose_name = "subscription"
        verbose_name_plural = "subscriptions"
