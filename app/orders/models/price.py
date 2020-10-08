from django.db import models

from core.behaviors import Amountable
from core.common_models import Common


class Price(Amountable, Common):
    """
    **Intermediate** model that holds a logic of pricing
    between item and service.

    Reference - https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ManyToManyField.through

    For example:
    - Dry clean on Pants price is 10$
    - Dry clean on T-shirts price is 5$
    """

    PCS = "pcs"
    LBS = "lbs"
    SQ_FT = "sq_ft"
    BAG = "bag"
    PLEAT = "pleat"
    UNIT_MAP = {
        PCS: "Piece",
        LBS: "Pound",
        SQ_FT: "Square Foot",
        BAG: "Bag",
        PLEAT: "Pleat",
    }
    UNIT_CHOICES = list(UNIT_MAP.items())

    service = models.ForeignKey(
        "orders.Service",
        verbose_name="service",
        related_name="price_list",
        on_delete=models.CASCADE,
    )
    item = models.ForeignKey(
        "orders.Item",
        verbose_name="item",
        related_name="price_list",
        on_delete=models.CASCADE,
    )

    # it usually mean a `pack`, `kit` or `set` of some
    # items that handles only in group.
    # for example:
    # - Suits [2 Pcs]
    # - Tuxedo [3 Pcs]
    # - Bed Sheet [Set] [4 PCs]
    count = models.PositiveSmallIntegerField(
        verbose_name="count of items",
        default=1,
    )
    unit = models.CharField(
        verbose_name="unit of item",
        max_length=10,
        choices=UNIT_CHOICES,
        default=PCS,
    )

    class Meta:
        verbose_name = "price"
        verbose_name_plural = "prices"
        unique_together = ("service", "item",)

    def __str__(self):
        return f"{self.service.title} on {self.item.title} = {self.dollar_amount} $"

    @property
    def pretty_unit(self):
        return self.get_unit_display()
