from django.contrib.auth import get_user_model

from djoser.views import UserViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainSlidingView

from api.v1_0.serializers import auth
from core.models import Phone
from core.services.signup import SignupService
from core.utils import get_clean_number

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
        phone = get_clean_number(raw_phone)

        service = SignupService()
        client = service.signup(email, password, phone)

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


class ForgotPasswordView(DjoserProxyView):
    response_serializer_class = auth.EmptyResponseSerializer
    proxy_action = {"post": "reset_password"}


class SetNewPasswordView(DjoserProxyView):
    response_serializer_class = auth.EmptyResponseSerializer
    proxy_action = {"post": "reset_password_confirm"}


class LoginView(TokenObtainSlidingView):
    response_serializer_class = auth.LoginResponseSerializer
