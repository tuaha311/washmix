from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.transaction import atomic

from billing.stripe_helper import StripeHelper
from notifications.models import Notification, NotificationTypes
from notifications.tasks import send_admin_client_information, send_email, send_sms
from users.models import Client

User = get_user_model()


class SignupService:
    def signup(self, email, password, phone) -> Client:
        with atomic():
            client = Client.objects.create_client(email, password, phone)
            client_id = client.id
            recipient_list = [client.email]

            stripe_helper = StripeHelper(client)
            customer = stripe_helper.customer

            client.stripe_id = customer["id"]
            client.save(update_fields={"stripe_id", "main_phone"})
        main_phone = client.main_phone.number

        send_email.send(
            event=settings.SIGNUP,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
            },
        )

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

        Notification.create_notification(client, NotificationTypes.NEW_SIGNUP)

        return client
