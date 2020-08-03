from copy import deepcopy

from django.core.management.base import BaseCommand

from core.models import Package

DEFAULT_PACKAGES = [
    {
        "name": "payc",
        "price": 0,
        "dry_clean": 0,
        "laundry": 0,
        "wash_fold": 0,
        "has_delivery": False,
        "has_welcome_box": False,
        "has_seasonal_garment": False,
        "has_credit_back": False,
    },
    {
        "name": "gold",
        "price": 99,
        "dry_clean": 10,
        "laundry": 5,
        "wash_fold": 5,
        "has_delivery": True,
        "has_welcome_box": True,
        "has_seasonal_garment": False,
        "has_credit_back": False,
    },
    {
        "name": "platinum",
        "price": 199,
        "dry_clean": 20,
        "laundry": 10,
        "wash_fold": 10,
        "has_delivery": True,
        "has_welcome_box": True,
        "has_seasonal_garment": True,
        "has_credit_back": True,
    },
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in DEFAULT_PACKAGES:
            clone = deepcopy(item)
            name = clone.pop("name")

            package, _ = Package.objects.get_or_create(name=name, defaults=item)

            print(f"{package} added")
