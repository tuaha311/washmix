from billing.models import Coupon, Invoice
from users.models import Client


class CouponHolder:
    def __init__(self, client: Client, invoice: Invoice):
        self._client = client
        self._invoice = invoice

    def apply_coupon(self, coupon: Coupon):
        self._invoice.coupon = coupon
        self._invoice.save()

        return self._invoice

    def _apply_by_amount(self):
        pass

    def _apply_by_percentage(self):
        pass
