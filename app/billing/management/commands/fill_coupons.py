from copy import deepcopy

from django.core.management.base import BaseCommand

from billing.models import Coupon
from settings.initial_info import COUPONS


class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in COUPONS:
            clone = deepcopy(item)
            code = clone.pop("code")

            coupon, _ = Coupon.objects.update_or_create(code=code, defaults=clone,)

            print(f"{coupon} added")
