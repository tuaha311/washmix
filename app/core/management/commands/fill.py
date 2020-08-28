from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        management.call_command("fill_packages")
        management.call_command("fill_cities")
        management.call_command("fill_prices")
        management.call_command("fill_admins")
        management.call_command("fill_coupons")
