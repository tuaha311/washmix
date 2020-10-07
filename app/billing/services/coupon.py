from billing.models import Coupon, Invoice

PERCENTAGE = 100


class CouponService:
    def __init__(self, invoice: Invoice, coupon: Coupon):
        self._invoice = invoice
        self._coupon = coupon

    def apply_coupon(self):
        coupon_handler = getattr(self, f"_apply_by_{self._coupon.discount_by}")
        amount, discount = coupon_handler()

        self._invoice.coupon = self._coupon
        self._invoice.amount = amount
        self._invoice.discount = discount
        self._invoice.save()

        return self._invoice

    def _apply_by_amount(self) -> tuple:
        amount = self._invoice.basic
        discount = self._coupon.value_off
        new_amount = amount - discount

        return new_amount, discount

    def _apply_by_percentage(self) -> tuple:
        amount = self._invoice.basic
        discount = amount * self._coupon.value_off / PERCENTAGE
        new_amount = amount - discount

        return new_amount, discount
