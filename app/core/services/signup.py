from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from billing.stripe_helper import StripeHelper
from core.tasks import send_email
from users.models import Client

User = get_user_model()


class SignupService:
    def signup(self, email, password, phone) -> Client:
        with atomic():
            client = Client.objects.create_client(email, password, phone)

            # TODO dramatiq add .send
            send_email(client.email, settings.SIGNUP)

            stripe_helper = StripeHelper(client)
            customer = stripe_helper.customer

            client.stripe_id = customer["id"]
            client.save()

        return client
