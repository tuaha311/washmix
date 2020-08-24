from functools import partial

from django.conf import settings
from django.contrib.auth import get_user_model

from djoser.views import UserViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.auth import SignupSerializer
from core.models import Phone
from notifications.senders.sendgrid import SendGridSender
from users.models import Client

User = get_user_model()


class EmailSendView(GenericAPIView):
    # TODO move to dramatiq
    def _send_email(self, email: str, name: str, event):
        sender = SendGridSender()
        sender.send(
            recipient_list=[email], event=event, context={"email": email, "name": name},
        )


class SignupView(EmailSendView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        phone = Phone.format_number(serializer.validated_data["phone"])

        client = Client.objects.create_client(email, password, phone)
        self._send_email(
            client.email, (client.first_name + " " + client.last_name).strip(), settings.SIGNUP
        )

        return Response({"email": client.email})


class ForgotPasswordView(UserViewSet):
    as_view = partial(UserViewSet.as_view, {"post": "reset_password"})


class SetNewPasswordView(UserViewSet):
    as_view = partial(UserViewSet.as_view, {"post": "reset_password_confirm"})
