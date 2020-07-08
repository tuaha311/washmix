from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework_expiring_authtoken.models import ExpiringToken
from rest_framework_expiring_authtoken.views import ObtainExpiringAuthToken

from api.serializers.users import UserDataSerializer
from core.models import CustomToken
from utilities.token import expired


class LoginUser(ObtainExpiringAuthToken):
    def post(self, request, *args, **kwargs):
        return self.process_request(request)
        # if response.status_code == HTTP_400_BAD_REQUEST:
        #     return response
        #
        # user = User.objects.get(email=request.data.get('username'))
        # if user:
        #     return Response({'token': response.data.get('token'),
        #                      'user': UserDataSerializer(user).data})

    def process_request(self, request):
        serializer = AuthTokenSerializer(data=request.data)

        token = None
        if serializer.is_valid():
            token, _ = ExpiringToken.objects.get_or_create(user=serializer.validated_data["user"])
            print("_----------------------", _, token.user)

        if token:
            is_long_lived = True
            try:
                CustomToken.objects.get(expiring_token=token)
            except CustomToken.DoesNotExist:
                is_long_lived = False

            if (not is_long_lived and token.expired()) or (
                is_long_lived and expired(token.created)
            ):
                # If the token is expired, generate a new one.
                token.delete()
                token = ExpiringToken.objects.create(user=serializer.validated_data["user"])

            if request.data.get("longLived"):
                CustomToken.objects.get_or_create(expiring_token=token)

            data = {"token": token.key, "user": UserDataSerializer(token.user).data}
            return Response(data)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
