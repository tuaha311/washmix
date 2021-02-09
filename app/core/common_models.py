from django.db import models


class Common(models.Model):
    created = models.DateTimeField(
        verbose_name="creation date and time", auto_now_add=True, editable=False,
    )
    changed = models.DateTimeField(
        verbose_name="last changed date and time", auto_now=True, editable=False,
    )

    class Meta:
        abstract = True


from core.behaviors import Amountable, Discountable
from core.mixins import CalculatedAmountWithDiscount, CalculatedDiscountMixin


class CommonAmountDiscountModel(Amountable, Discountable, CalculatedAmountWithDiscount, CalculatedDiscountMixin, Common):
    class Meta:
        abstract = True
