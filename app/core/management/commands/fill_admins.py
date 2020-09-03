from django.core.management.base import BaseCommand
from django.db import IntegrityError

from settings.initial_info import ADMINS
from users.models import Client


class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in ADMINS:
            try:
                client = Client.objects.create_client(**item)
                print(f"{client} added")
            except IntegrityError:
                email = item["email"]
                print(f"{email} already exists")
