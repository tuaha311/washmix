from django.core.management.base import BaseCommand

from core.models import Package
from modules.enums import PACKAGE_NAMES


class Command(BaseCommand):
    def handle(self, *args, **options):
        for name, price in PACKAGE_NAMES.items():
            try:
                package = Package.objects.get(name=name)
                package.price = price
                package.save()
            except Package.DoesNotExist:
                kwargs = {"name": name, "price": price}
                Package.objects.create(**kwargs)
