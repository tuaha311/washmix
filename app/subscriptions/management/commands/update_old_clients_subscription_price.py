from django.core.management.base import BaseCommand

from subscriptions.models import Package
from users.models import Client


class Command(BaseCommand):
    help = "update the old subscription delivery_free_from with new packages delivery_free_from"

    def handle(self, *args, **kwargs):
        for package in Package.objects.all():
            for client in Client.objects.filter(subscription__name=package.name):
                client.subscription.delivery_free_from = package.delivery_free_from
                client.subscription.save()
