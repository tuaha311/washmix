from django.db import models
from django.utils.timezone import localtime

from core.common_models import Common
from legacy.enums import CouponType


class Coupon(Common):
    """
    Coupon (also called "Promocode") that we provide to our clients.
    Coupon can give some discount on our services.
    """

    PERCENTAGE = "percentage"
    AMOUNT = "amount"
    DISCOUNT_BY_MAP = {
        PERCENTAGE: "Discount by percentage",
        AMOUNT: "Discount by amount",
    }
    DISCOUNT_BY_CHOICES = list(DISCOUNT_BY_MAP.items())

    code = models.CharField(
        verbose_name="code",
        max_length=30,
        unique=True,
    )
    description = models.CharField(
        verbose_name="description or note for coupon",
        max_length=200,
        blank=True,
    )
    discount_by = models.CharField(
        max_length=10,
        choices=DISCOUNT_BY_CHOICES,
        default=AMOUNT,
    )
    value_off = models.BigIntegerField(
        verbose_name="value of discount",
        help_text=("for discount by percentage - it will be percentage in % of discount;\n"
                   "for discount by amount - it will be amount in cents (¢) of discount"),
        default=0,
    )
    end_date = models.DateTimeField(
        verbose_name="end date of coupon",
        default=localtime,
    )
    is_valid = models.BooleanField(
        verbose_name="is coupon valid for apply",
        default=True,
    )
    max_redemptions = models.IntegerField(
        verbose_name="maximum count of redemptions",
        default=1,
    )
    kind = models.CharField(
        verbose_name="coupon type",
        max_length=30,
        choices=[(item, item.value) for item in CouponType],
        null=True,
        default=CouponType.FIRST.value,
    )

    class Meta:
        verbose_name = "coupon"
        verbose_name_plural = "coupons"

    def __str__(self):
        return self.code
