from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from billing.services.checkout import WelcomeService
from billing.stripe_helper import StripeHelper
from users.models import Client

User = get_user_model()


class SignupService:
    def signup(self, zipCode, address, email, password, phone) -> Client:
        with atomic():
            client = Client.objects.create_client(email, password, phone)
            stripe_helper = StripeHelper(client)
            customer = stripe_helper.customer

            client.stripe_id = customer["id"]
            client.save(update_fields={"stripe_id", "main_phone"})

            service = WelcomeService(client, None, None)
            raw_address = {"zip_code": zipCode, "address_line_1": address}
            address = service._create_signup_main_address(raw_address)

        return client
