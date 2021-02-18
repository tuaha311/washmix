from django.contrib.auth import get_user_model
from django.utils.timezone import now

from djoser.conf import settings as djoser_settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainSlidingView

from api.client.serializers import auth
from api.utils import cleanup_email, get_custom_user_email
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
        clean_email = cleanup_email(email)
        phone = get_clean_number(raw_phone)

        service = SignupService()
        client = service.signup(clean_email, password, phone)

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
    empty_response = True
    response_serializer_class = auth.EmptyResponseSerializer
    proxy_action = {"post": "reset_password"}

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        """
        Custom implementation from `djoser.views.UserViewSet.reset_password`.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = {"user": user}
            email = get_custom_user_email(user)
            clean_email = cleanup_email(email)
            to = [clean_email]
            djoser_settings.EMAIL.password_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)


class SetNewPasswordView(DjoserProxyView):
    empty_response = True
    response_serializer_class = auth.EmptyResponseSerializer
    proxy_action = {"post": "reset_password_confirm"}

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        """
        Custom implementation from `djoser.views.UserViewSet.reset_password_confirm`.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            email = get_custom_user_email(serializer.user)
            clean_email = cleanup_email(email)
            to = [clean_email]
            djoser_settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(TokenObtainSlidingView):
    response_serializer_class = auth.LoginResponseSerializer
