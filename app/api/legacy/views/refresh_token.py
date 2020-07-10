from django.conf import settings

from oauth2_provider.admin import AccessToken, Application
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, permissions
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_social_oauth2.views import TokenView

from api.legacy.serializers.users import UserDataSerializer
from modules.enums import SignUp
from modules.helpers import StripeHelper
from modules.oauth import get_user_by_email, get_user_from_token

# OAUTH TOOLKIT ID AND SECRET
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET


class RefreshTokenView(TokenView):
    def post(self, request, *args, **kwargs):
        request.data.update({"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
        response = super(RefreshTokenView, self).post(request, *args, **kwargs).data
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
