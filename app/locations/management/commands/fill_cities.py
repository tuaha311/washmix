from django.core.management.base import BaseCommand

from locations.models import City, ZipCode

DEFAULT_CITIES_WITH_ZIP_CODES = [
    {"name": "New York", "zip_codes": [1234, 5678,],},
    {"name": "Boston", "zip_codes": ["ABCD", "EFGH",]},
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in DEFAULT_CITIES_WITH_ZIP_CODES:
            city, _ = City.objects.get_or_create(name=item["name"])

            for element in item["zip_codes"]:
                zip_code, _ = ZipCode.objects.get_or_create(city=city, value=element,)

            print(f"{zip_code} added for {city}")
