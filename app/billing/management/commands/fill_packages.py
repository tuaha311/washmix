from copy import deepcopy

from django.core.management.base import BaseCommand
from django.db import transaction

from billing.models import Package
from settings.initial_info import PACKAGES


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            for item in PACKAGES:
                clone = deepcopy(item)
                name = clone.pop("name")

                package, _ = Package.objects.update_or_create(name=name, defaults=clone)

                print(f"{package} added")
