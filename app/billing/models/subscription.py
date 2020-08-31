from django.conf import settings
from django.db import models

from billing.common_models import CommonPackageSubscription
from core.common_models import Common


class SubscriptionManager(models.Manager):
    def create_and_fill(self, package, invoice):
        system_fields = ["id", "created", "changed"]

        for field in package._meta.get_fields():
            if field in system_fields:
                continue

            subscription = self.model(invoice=invoice)
            package_field_value = getattr(package, field)
            setattr(subscription, field, package_field_value)

            subscription.save()

            return subscription


class Subscription(CommonPackageSubscription, Common):
    """
    Concrete instance of Package.
    It holds all the field of Package, and can be interpreted as
    per user conditions of Package.
    """

    name = models.CharField(
        verbose_name="name",
        max_length=20,
        choices=settings.PACKAGE_NAME_CHOICES,
    )
    invoice = models.OneToOneField(
        "billing.Invoice",
        verbose_name="invoice",
        related_name="subscription",
        on_delete=models.CASCADE,
    )

    objects = SubscriptionManager()

    class Meta:
        verbose_name = "subscription"
        verbose_name_plural = "subscriptions"
