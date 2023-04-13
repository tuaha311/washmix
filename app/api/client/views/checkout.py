import logging

from django.conf import settings

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from api.client.serializers.checkout import (
    WelcomeCheckoutResponseSerializer,
    WelcomeCheckoutSerializer,
)
from archived.models import ArchivedCustomer
from billing.services.checkout import WelcomeService
from notifications.models import Notification, NotificationTypes
from notifications.tasks import send_admin_client_information, send_email, send_sms

logger = logging.getLogger(__name__)


class WelcomeCheckoutView(GenericAPIView):
    serializer_class = WelcomeCheckoutSerializer
    response_serializer_class = WelcomeCheckoutResponseSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data["order"]
        user = serializer.validated_data["user"]
        raw_address = serializer.validated_data["address"]
        raw_billing_address = serializer.validated_data["billing_address"]

        client = request.user.client
        welcome_service = WelcomeService(client, request, order)
        address, billing_address = welcome_service.checkout(user, raw_address, raw_billing_address)

        # Deleting User Data if the client was already in our archived Customer
        archived_customer = ArchivedCustomer.objects.filter(email=client.email).delete()
        # Confirming that the deletion was successful
        if archived_customer[0] > 0:
            logger.info(
                f"{archived_customer[0]} records for {client.email} were successfully deleted."
            )
        else:
            logger.info(f"No records found for {client.email}. Nothing was deleted.")

        # Send the Welcome email to the user
        self.send_welcome_email(client)

        response_body = {
            "user": user,
            "address": address,
            "billing_address": billing_address,
        }
        response = self.response_serializer_class(response_body).data

        return Response(response)

    def send_welcome_email(self, client):
        main_phone = client.main_phone.number
        client_id = client.id
        recipient_list = [client.email]

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
