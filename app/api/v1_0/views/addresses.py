from rest_framework.viewsets import ModelViewSet

from api.v1_0.mixins import MainAttributeMixin
from api.v1_0.serializers.addresses import AddressSerializer


class AddressViewSet(MainAttributeMixin, ModelViewSet):
    """
    Methods to manipulate with `Address` entity
    """

    serializer_class = AddressSerializer
    main_attribute = "main_address"

    def get_queryset(self):
        return self.request.user.client.address_list.all()
