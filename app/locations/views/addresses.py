from rest_framework.viewsets import ModelViewSet

from api.v1_0.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from locations.serializers.addresses import AddressSerializer


class AddressViewSet(PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin, ModelViewSet):
    """
    Methods to manipulate with `Address` entity
    """

    serializer_class = AddressSerializer
    main_attribute = "main_address"

    def get_queryset(self):
        client = self.request.user.client
        return client.address_list.all()
