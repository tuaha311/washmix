from django.db import models
from django.utils.timezone import localtime

from core.common_models import Common
from modules.enums import CouponType


class Coupon(Common):
    """
    Coupon (also called "Promocode") that we provide to our clients.
    Coupon can give some discount on our services.
    """

    name = models.CharField(
        verbose_name="name of coupon",
        max_length=30,)
    amount_off = models.DecimalField(
        verbose_name="amount off",
        max_digits=9,
        decimal_places=2,
        default=0,
    )
    percentage_off = models.DecimalField(
        verbose_name="percentage off",
        max_digits=9,
        decimal_places=2,
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
