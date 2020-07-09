import logging
from datetime import datetime, timedelta

from django.conf import settings

import pytz
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_social_oauth2.authentication import SocialAuthentication

from api.permissions import CustomIsAdminUser, IsAuthenticatedOrPost, RefreshTokenAuthentication
from api.serializers.users import UserDataSerializer
from modules.oauth import convert_to_auth_token, get_user_from_token

logging.basicConfig(level=logging.ERROR, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# from rest_framework.authentication import TokenAuthentication
# from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

# GOOGLE ID AND SECRET
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET

# OAUTH TOOLKIT ID AND SECRET
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET


class OAuth(APIView):
    authentication_classes = (RefreshTokenAuthentication, SocialAuthentication)
    permission_classes = (IsAuthenticatedOrPost, CustomIsAdminUser)

    def post(self, request, *args, **kwargs):
        """
        This api is to add Fedrated (Google/Facebook) Users in our system and returns access_token, refresh_token and user object.
        If user is already present in database, it simply create credentials and return those credentials
        {
            "backend": "google-oauth2",
            "token": ""ya29.GlyXBipIbk0yYSAojOUj05l50rZR4GFLIXL_rdR33TbtCiPbtzevnq5C9h3BC6X6jTYSAuzp_URfO00ae4L_EZMcDW6GzarZBGED7HQCqQXE52OjDIJvTflMlzBVRw
        }
        All the fields mentioned in json are a must.
        :return: access_token, refresh_toke, user.
        """
        data = request.data
        backend = data["backend"]
        token = data["token"]
        error_codes = {"access_denied": status.HTTP_401_UNAUTHORIZED}
        response = convert_to_auth_token(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, backend=backend, token=token,
        )
        print("response", response)
        if "error" in response:

            return Response(
                {"error": response.get("error_description", "Something went wrong")},
                status=error_codes.get(response["error"], status.HTTP_400_BAD_REQUEST),
            )
        user = get_user_from_token(response)
        timezone = pytz.timezone("UTC")
        print("User", timezone.localize(datetime.utcnow()) - user.date_joined)

        return Response(
            {
                "token": response["access_token"],
                "refresh_token": response["refresh_token"],
                "user": UserDataSerializer(user).data,
                "created": (timezone.localize(datetime.utcnow()) - user.date_joined)
                < timedelta(seconds=10),
            },
            status=status.HTTP_201_CREATED
            if (timezone.localize(datetime.utcnow()) - user.date_joined) < timedelta(seconds=10)
            else status.HTTP_200_OK,
        )
