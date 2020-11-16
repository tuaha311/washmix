from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from billing.stripe_helper import StripeHelper
from notifications.tasks import send_email
from users.models import Client

User = get_user_model()


class SignupService:
    def signup(self, email, password, phone) -> Client:
        with atomic():
            client = Client.objects.create_client(email, password, phone)
            client_id = client.id

            send_email.send(
                client_id=client_id,
                event=settings.SIGNUP,
            )

            stripe_helper = StripeHelper(client)
            customer = stripe_helper.customer

            client.stripe_id = customer["id"]
            client.save()

        return client
