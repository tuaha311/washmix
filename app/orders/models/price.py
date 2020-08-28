from django.db import models

from core.behaviors import Valuable
from core.common_models import Common


class Price(Valuable, Common):
    """
    Intermediate model that holds a logic of pricing
    between item and service.

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
        return f"{self.service.title} on {self.item.title} = {self.dollar_value} $"
