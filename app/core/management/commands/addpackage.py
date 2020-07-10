from django.core.management.base import BaseCommand

from core.models import Package
from modules.enums import PACKAGE_NAMES


class Command(BaseCommand):
    def handle(self, *args, **options):
        for name, price in PACKAGE_NAMES.items():
            try:
                package = Package.objects.get(package_name=name)
                package.package_price = price
                package.save()
            except Package.DoesNotExist:
                kwargs = {"package_name": name, "package_price": price}
                Package.objects.create(**kwargs)
