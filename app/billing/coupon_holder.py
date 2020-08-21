from billing.models import Coupon
from users.models import Client


class CouponHolder:
    def __init__(self, client: Client):
        self._client = client

    def apply_coupon(self, coupon: Coupon):
        pass
