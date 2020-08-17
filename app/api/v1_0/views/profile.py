from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request

from api.v1_0.serializers.profile import ProfileSerializer


class ProfileView(GenericAPIView):
    serializer_class = ProfileSerializer

    def get(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user.client)

        return Response(serializer.data)
