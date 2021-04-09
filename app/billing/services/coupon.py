from django.conf import settings

from billing.models import Coupon

PERCENTAGE = 100


class CouponService:
    def __init__(self, amount: int, coupon: Coupon):
        self._amount = amount
        self._coupon = coupon

    def calculate_coupon_discount(self):
        if not self._coupon:
            return settings.DEFAULT_ZERO_DISCOUNT

        coupon_handler = getattr(self, f"_calculate_by_{self._coupon.discount_by}")
        discount = coupon_handler()

        return discount

    def _calculate_by_amount(self) -> float:
        amount = self._amount
        discount = self._coupon.value_off

        # discount can't be bigger that amount
        if discount > amount:
            return amount

        return discount

    def _calculate_by_percentage(self) -> float:
        amount = self._amount
        discount = amount * self._coupon.value_off / PERCENTAGE

        return discount
