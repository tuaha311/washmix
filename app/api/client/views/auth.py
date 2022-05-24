from django.contrib.auth import get_user_model

from djoser.views import UserViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainSlidingView

from api.client.serializers import auth
from api.client.serializers.auth import (
    DjoserPasswordResetConfirmSerializer,
    DjoserSendEmailResetSerializer,
)
from api.utils import cleanup_email
from core.services.signup import SignupService
from core.utils import get_clean_number
from locations.models import Address

User = get_user_model()


class SignupView(GenericAPIView):
    serializer_class = auth.SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        raw_phone = serializer.validated_data["phone"]
        # address =serializer.validated_data["address"]
        clean_email = cleanup_email(email)
        clean_phone = get_clean_number(raw_phone)

        service = SignupService()
        client = service.signup(clean_email, password, clean_phone)

        return Response({"email": client.email})


class DjoserProxyView(UserViewSet):
    """
    We are using this view to proxy all behavior and methods
    to Djoser. Djoser has already implemented auth cases, but it has
    some messy implementation in 1 viewset. Instead of using this
    awkward viewset - we splitting this behavior into atomic views.
    """

    proxy_action: dict

    @classmethod
    def as_view(cls, actions=None, **initkwargs):
        view = super().as_view(cls.proxy_action)
        return view


class DjoserForgotPasswordView(DjoserProxyView):
    empty_response = True
    response_serializer_class = auth.EmptyResponseSerializer
    proxy_action = {"post": "reset_password"}

    def get_serializer_class(self):
        return DjoserSendEmailResetSerializer


class DjoserSetNewPasswordView(DjoserProxyView):
    empty_response = True
    response_serializer_class = auth.EmptyResponseSerializer
    proxy_action = {"post": "reset_password_confirm"}

    def get_serializer_class(self):
        return DjoserPasswordResetConfirmSerializer


class LoginView(TokenObtainSlidingView):
    response_serializer_class = auth.LoginResponseSerializer
