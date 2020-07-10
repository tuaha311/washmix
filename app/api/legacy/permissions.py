from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

from rest_framework.permissions import IsAdminUser, IsAuthenticated

from modules.enums import AppUsers


class IsAuthenticatedOrPost(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return super(IsAuthenticatedOrPost, self).has_permission(request, view)


class IsAuthenticatedOrAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == "PATCH" and request.user.is_staff:
            return False
        return super(IsAuthenticatedOrAdmin, self).has_permission(request, view)


class CustomIsAdminUser(IsAdminUser):
    """This permission check allows 'POST' 'PATCH' 'PUT' and checks if incoming request has 
    user as admin. This permission allows only admin user to view all non admin user records"""

    def has_permission(self, request, view):
        if (
            request.method == "POST"
            and hasattr(request.user, "profile")
            and (
                request.user.profile.app_users == AppUsers.EMPLOYEE.value
                or request.user.profile.app_users == AppUsers.REGULAR_USERS.value
            )
        ):
            return False
        if request.method in ["POST", "PATCH", "PUT"]:
            return True
        if not request.user.is_staff:
            return request.user.id == int(view.kwargs.get("id") or -1)
        return True

    def has_object_permission(self, request, view, obj):
        pass


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)


account_activation_token = TokenGenerator()
