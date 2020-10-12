from rest_framework.generics import RetrieveUpdateAPIView

from users.v1.serializers.profile import ProfileSerializer


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.client
