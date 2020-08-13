from django.core.management.base import BaseCommand
from django.db import transaction

from orders.models import Item, Price, Service

PRICE_LIST = [
    {
        "service": "Dry Cleaning",
        "item_list": [
            {
                "item": "Pants",
                "is_visible": True,
                "price": {"value": 10, "count": 1, "unit": Price.PCS},
            },
            {
                "item": "Shirt",
                "is_visible": False,
                "price": {"value": 5, "count": 1, "unit": Price.LBS,},
            },
        ],
    },
    {
        "service": "Laundry",
        "item_list": [
            {
                "item": "Coat",
                "is_visible": True,
                "price": {"value": 19, "count": 2, "unit": Price.PCS},
            },
        ],
    },
    {
        "service": "Alterations & Repair",
        "item_list": [
            {
                "item": "Zipper Repair",
                "is_visible": True,
                "price": {"value": 29, "count": 1, "unit": Price.PCS},
            },
        ],
    },
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            for raw_service in PRICE_LIST:
                service, _ = Service.objects.update_or_create(title=raw_service["service"],)
                print(f"service {service} added")

                for raw_item in raw_service["item_list"]:
                    item, _ = Item.objects.update_or_create(
                        title=raw_item["item"], defaults={"is_visible": raw_item["is_visible"],}
                    )
                    print(f"item {item} added")

                    raw_price = raw_item["price"]
                    price, _ = Price.objects.update_or_create(
                        service=service,
                        item=item,
                        defaults={
                            "value": raw_price["value"],
                            "count": raw_price["count"],
                            "unit": raw_price["unit"],
                        },
                    )
                    print(f"price {price} added")
