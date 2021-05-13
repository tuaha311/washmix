from django.conf import settings

from rest_framework.generics import RetrieveUpdateAPIView

from api.mixins import ProxyFieldsOnModelUpdate
from users.api.serializers.profile import ProfileSerializer


class ProfileRetrieveUpdateView(ProxyFieldsOnModelUpdate, RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    proxy_fields = settings.UPDATE_FIELDS_FOR_USER

    def get_object(self):
        return self.request.user.client
