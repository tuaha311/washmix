from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from core.behaviors import Amountable
from core.common_models import Common


class Invoice(Amountable, Common):
    """
    Invoice that we generated for buying package or order.

    Most of time, we use `object_id` to point on tables:
        - orders.Order
        - billing.Package
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        related_name="invoice_list",
        on_delete=models.CASCADE,
    )
    coupon = models.ForeignKey(
        "billing.Coupon",
        verbose_name="coupon",
        related_name="invoice_list",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    card = models.ForeignKey(
        "billing.Card",
        verbose_name="card",
        related_name="invoice_list",
        on_delete=models.SET_NULL,
        null=True,
    )

    amount = models.BigIntegerField(
        verbose_name="amount in cents",
        blank=True,
        null=True,
    )

    # field `object` just a wrapper around
    # `content_type` and `object_id` for convenient
    # querying and transforming polymorphic key into
    # real object. field `object` doesn't stored inside db.
    # reference - https://docs.djangoproject.com/en/2.2/ref/contrib/contenttypes/#generic-relations
    _content_type = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    _object_id = models.PositiveIntegerField(
        verbose_name="ID of related object",
        blank=True,
        null=True,
    )
    # TODO переименовать - object очень похоже на objects
    entity = GenericForeignKey(
        "_content_type", "_object_id",
    )

    class Meta:
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

    def __str__(self):
        return f"№ {self.pk} {self.amount}"

    @property
    def is_filled(self):
        required_fields = [self.card, self.amount, self.entity]
        return all(required_fields)

    @property
    def package(self):
        try:
            if self._content_type.model == "package":
                return self.entity
        except AttributeError:
            return None

    @property
    def order(self):
        return None

    @property
    def discount(self):
        return None
