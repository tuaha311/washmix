from oauth2_provider.backends import OAuth2Backend
from rest_framework import exceptions, HTTP_HEADER_ENCODING
from rest_framework.authentication import (
    get_authorization_header
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser
)
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework_expiring_authtoken.models import ExpiringToken

from app.modules.constant import AppUsers
from ..models.models import CustomToken
from ..utilities.token import expired


class IsAuthenticatedOrPost(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return super(IsAuthenticatedOrPost, self).has_permission(request, view)


class IsAuthenticatedOrAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'PATCH' and request.user.is_staff:
            return False
        return super(IsAuthenticatedOrAdmin, self).has_permission(request, view)


class CustomIsAdminUser(IsAdminUser):
    """This permission check allows 'POST' 'PATCH' 'PUT' and checks if incoming request has 
    user as admin. This permission allows only admin user to view all non admin user records"""
    def has_permission(self, request, view):
        if request.method == 'POST' and hasattr(request.user, 'profile') and (request.user.profile.app_users == AppUsers.EMPLOYEE.value or \
                        request.user.profile.app_users == AppUsers.REGULAR_USERS.value):
            return False
        if request.method in ['POST', 'PATCH', 'PUT']:
            return True
        if not request.user.is_staff:
            return request.user.id == int(view.kwargs.get('id') or -1)
        return True


    def has_object_permission(self, request, view, obj):
        pass


class RefreshTokenAuthentication(ExpiringTokenAuthentication):
    model = ExpiringToken

    def authenticate_credentials(self, key):
        try:
            is_custom = False
            token = self.model.objects.get(key=key)
            try:
                CustomToken.objects.get(expiring_token=token)
                is_custom = True
            except CustomToken.DoesNotExist:
                pass

        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        if (not is_custom and token.expired()) or (is_custom and expired(token.created)):
            raise exceptions.AuthenticationFailed('Token has expired')

        return (token.user, token)


class CustomSocialAuthentication(OAuth2Backend):
    def authenticate(self, request):

        auth_header = get_authorization_header(request).decode(HTTP_HEADER_ENCODING)
        auth = auth_header.split()

        if not auth or auth[0].lower() != 'bearer':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 3:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        response = super(CustomSocialAuthentication, self).authenticate(request=request)
        if not response:
            return response

        token = auth[1]
        return response, token


from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()
