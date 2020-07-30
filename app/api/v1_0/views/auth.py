from functools import partial

from djoser.views import UserViewSet


class SignupView(UserViewSet):
    as_view = partial(UserViewSet.as_view, {"post": "create"})


class ForgotPasswordView(UserViewSet):
    as_view = partial(UserViewSet.as_view, {"post": "reset_password"})


class SetNewPasswordView(UserViewSet):
    as_view = partial(UserViewSet.as_view, {"post": "reset_password_confirm"})
