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
            recipient_list = [client.email]

            send_email.send(
                event=settings.SIGNUP,
                recipient_list=recipient_list,
                extra_context={
                    "client_id": client_id,
                },
            )

            stripe_helper = StripeHelper(client)
            customer = stripe_helper.customer

            client.stripe_id = customer["id"]
            client.save()

        return client
