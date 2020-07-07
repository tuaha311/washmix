from ..commands import *
from oauth2_provider.models import Application
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Creating Auth Application...")
        user = User.objects.get(
            email="admin@washmix.com"
        )

        Application.objects.create(
            user=user,
            client_type='confidential',
            authorization_grant_type='password',
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            skip_authorization=True
        )
        print('Auth application created successfully')
