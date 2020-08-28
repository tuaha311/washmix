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

    # Field `entity` just a wrapper around
    # `_content_type` and `_entity_id` for convenient
    # querying and transforming polymorphic key into
    # real object. Field `entity` doesn't stored inside db.
    #
    # Also, we don't use `_content_type` and `_entity_id` directly -
    # and because of this reason, they marked as private attributes.
    #
    # Word `object` was not used because it is very similar to word `objects` -
    # which is a Manager. To avoid typing or understanding errors we
    # called it as `entity`.
    #
    # Reference - https://docs.djangoproject.com/en/2.2/ref/contrib/contenttypes/#generic-relations
    _content_type = models.ForeignKey(
        "contenttypes.ContentType",
        verbose_name="content type of related object",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    _entity_id = models.PositiveIntegerField(
        verbose_name="ID of related object",
        blank=True,
        null=True,
    )
    entity = GenericForeignKey(
        "_content_type", "_entity_id",
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

    @property
    def dollar_discount(self):
        return None

    @property
    def total(self):
        return None
