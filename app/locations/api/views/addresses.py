from django.conf import settings

from rest_framework.viewsets import ModelViewSet

from api.client.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from api.mixins import ProxyFieldsOnModelUpdate
from locations.api.serializers.addresses import AddressSerializer


class AddressViewSet(
    ProxyFieldsOnModelUpdate,
    PreventDeletionOfMainAttributeMixin,
    SetMainAttributeMixin,
    ModelViewSet,
):
    """
    Methods to manipulate with `Address` entity
    """

    serializer_class = AddressSerializer
    main_attribute = "main_address"
    proxy_fields = settings.UPDATE_FIELDS_FOR_ADDRESS

    def get_queryset(self):
        client = self.request.user.client
        return client.address_list.all()
