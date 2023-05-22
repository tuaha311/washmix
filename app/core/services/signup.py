from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from billing.services.checkout import WelcomeService
from billing.stripe_helper import StripeHelper
from notifications.tasks import send_admin_client_information, send_sms
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

        main_phone = client.main_phone.number
        send_admin_client_information(client.id, "New User Signed Up")
        send_sms.send_with_options(
            kwargs={
                "event": settings.USER_SIGNUP,
                "recipient_list": [main_phone],
                "extra_context": {
                    "client_id": client.id,
                },
            },
            delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
        )
        return client
