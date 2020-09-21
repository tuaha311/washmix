from django.db import models

from core.behaviors import Priceable
from core.common_models import Common


class History(Priceable, Common):
    """
    Historical price log model.

    It helps to remember exact price on exact service with item for
    exact date and time.

    For example:
    - I bought Wash & Fold on my Pants for 4$ one year ago.
    - Today admin raises price on Wash & Fold service with Pants up to 7$
    - My previous order will still have an 4$ total.
    """

    service = models.CharField(
        verbose_name="name of service",
        max_length=300,
    )
    item = models.CharField(
        verbose_name="name of item",
        max_length=300,
    )

    class Meta:
        verbose_name = "basket"
        verbose_name_plural = "baskets"




