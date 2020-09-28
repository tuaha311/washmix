from django.core.management.base import BaseCommand
from django.db import transaction

from locations.models import City, ZipCode
from settings.initial_info import CITIES


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            for item in CITIES:
                city, _ = City.objects.update_or_create(name=item["name"])

                for element in item["zip_codes"]:
                    zip_code, _ = ZipCode.objects.update_or_create(value=element)
                    city.zip_code_list.add(zip_code)

                print(f"{zip_code} added for {city}")
