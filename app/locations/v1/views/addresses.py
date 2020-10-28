from rest_framework.viewsets import ModelViewSet

from api.client.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from locations.v1.serializers.addresses import AddressSerializer


class AddressViewSet(PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin, ModelViewSet):
    """
    Methods to manipulate with `Address` entity
    """

    serializer_class = AddressSerializer
    main_attribute = "main_address"

    def get_queryset(self):
        client = self.request.user.client
        return client.address_list.all()
