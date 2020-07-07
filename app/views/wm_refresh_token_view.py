from core.models import CustomToken
from django.conf import settings
from modules.constant import SignUp
from modules.helpers import StripeHelper
from modules.oauth import get_user_by_email, get_user_from_token
from oauth2_provider.admin import AccessToken, Application
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, permissions
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_expiring_authtoken.models import ExpiringToken
from rest_framework_social_oauth2.views import TokenView
from serializer.refresh_token_serializer import RefreshTokenSerializer
from serializer.user_serializer import UserDataSerializer
from utilities.token import expired

# OAUTH TOOLKIT ID AND SECRET
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET


class AppRefreshTokenView(APIView):
    def post(self, request, **kwargs):

        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        user = serializer.validated_data["user"]

        is_long_lived = True
        try:
            CustomToken.objects.get(expiring_token=token)
        except CustomToken.DoesNotExist:
            is_long_lived = False

        if (not is_long_lived and token.expired()) or (is_long_lived and expired(token.created)):
            token.delete()
            token = ExpiringToken.objects.create(user=serializer.validated_data["user"])
        if request.data.get("longLived"):
            CustomToken.objects.get_or_create(expiring_token=token)

        return Response(data={"token": token.key, "user_id": user.id})


class SocialAppLoginRefreshTokenView(TokenView):
    def post(self, request, *args, **kwargs):
        request.data.update({"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
        response = super(SocialAppLoginRefreshTokenView, self).post(request, *args, **kwargs).data
        social_user = None
        if "error" in response:
            social_user = get_user_by_email(request.data.get("username"))
            if not social_user:
                raise AuthenticationFailed(
                    response.get("error_description", "") or response.get("error", "")
                )
        else:
            user = get_user_from_token(response)

        if not social_user:
            return Response(
                {
                    "token": response["access_token"],
                    "refresh_token": response["refresh_token"],
                    "user": UserDataSerializer(instance=user, stripes_helper=StripeHelper()).data,
                    "signup_type": SignUp.washmix.value,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "token": "",
                "refresh_token": "",
                "user": UserDataSerializer(
                    instance=social_user, stripes_helper=StripeHelper()
                ).data,
                "signup_type": social_user.profile.authentication_provider,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@authentication_classes([OAuth2Authentication])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    try:
        app = Application.objects.get(client_id=CLIENT_ID)
    except Application.DoesNotExist:
        return Response(
            {"detail": "The application linked to the provided client_id could not be found."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tokens = AccessToken.objects.filter(user=request.user, application=app)
    tokens.delete()
    return Response({}, status=status.HTTP_204_NO_CONTENT)
