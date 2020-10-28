from rest_framework.viewsets import ModelViewSet

from api.client.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from core.api.serializers import PhoneSerializer


class PhoneViewSet(PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin, ModelViewSet):
    """
    Methods to manipulate with `Address` entity.
    """

    serializer_class = PhoneSerializer
    main_attribute = "main_phone"

    def get_queryset(self):
        client = self.request.user.client
        return client.phone_list.all()
