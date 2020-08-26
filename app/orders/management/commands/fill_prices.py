from django.core.management.base import BaseCommand
from django.db import transaction

from orders.models import Item, Price, Service
from settings.initial_info import PRICES


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            for raw_service in PRICES:
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
