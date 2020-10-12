from rest_framework.viewsets import ModelViewSet

from api.v1_0.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from core.v1.serializers import PhoneSerializer


class PhoneViewSet(PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin, ModelViewSet):
    """
    Methods to manipulate with `Address` entity.
    """

    serializer_class = PhoneSerializer
    attribute_name = "main_phone"

    def get_queryset(self):
        return self.request.user.client.phone_list.all()
