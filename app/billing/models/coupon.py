from django.db import models
from django.utils.timezone import localtime

from billing.choices import InvoiceDiscountBy
from core.common_models import Common


class Coupon(Common):
    """
    Client-side entity.

    Coupon (also called "Promocode") that we provide to our clients.
    Coupon can give some discount on our services.
    """

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
        choices=InvoiceDiscountBy.CHOICES,
        default=InvoiceDiscountBy.AMOUNT,
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

    class Meta:
        verbose_name = "coupon"
        verbose_name_plural = "coupons"

    def __str__(self):
        return self.code
