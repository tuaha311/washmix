from django.conf import settings

from rest_framework.viewsets import ModelViewSet

from api.client.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from locations.api.serializers.addresses import AddressSerializer


class AddressViewSet(PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin, ModelViewSet):
    """
    Methods to manipulate with `Address` entity
    """

    serializer_class = AddressSerializer
    main_attribute = "main_address"

    def perform_update(self, serializer):
        address = serializer.instance

        update_fields = {}
        unique_fields = set(serializer.validated_data.keys())
        if settings.UPDATE_FIELDS_FOR_ADDRESS & unique_fields:
            update_fields = settings.UPDATE_FIELDS_FOR_ADDRESS

        super().perform_update(serializer)

        address.save(update_fields=update_fields)

    def get_queryset(self):
        client = self.request.user.client
        return client.address_list.all()
