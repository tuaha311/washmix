from django.core.management.base import BaseCommand
from django.db import IntegrityError

from users.models import Client

DEFAULT_ADMINS = [
    {
        "email": "api@evrone.com",
        "password": "helloevrone",
        "number": "12001230210",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "email": "ds.ionin@evrone.com",
        "password": "helloevrone",
        "number": "12001230211",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "email": "savoskin@evrone.com",
        "password": "helloevrone",
        "number": "12001230212",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "email": "og@evrone.com",
        "password": "helloevrone",
        "number": "12001230213",
        "is_superuser": True,
        "is_staff": True,
    },
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in DEFAULT_ADMINS:
            try:
                client = Client.objects.create_client(**item)
                print(f"{client} added")
            except IntegrityError:
                email = item["email"]
                print(f"{email} already exists")
