from functools import partial

from django.contrib.auth import get_user_model

from djoser.views import UserViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1_0.serializers.auth import SignupSerializer
from core.models import Phone
from core.services.signup import SignupService

User = get_user_model()


class SignupView(GenericAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        phone = Phone.format_number(serializer.validated_data["phone"])

        service = SignupService()
        client = service.signup(email, password, phone)

        return Response({"email": client.email})


class ForgotPasswordView(UserViewSet):
    as_view = partial(UserViewSet.as_view, {"post": "reset_password"})


class SetNewPasswordView(UserViewSet):
    as_view = partial(UserViewSet.as_view, {"post": "reset_password_confirm"})
