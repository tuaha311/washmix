from rest_framework.viewsets import ModelViewSet

from api.client.mixins import PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin
from core.api.serializers import PhoneSerializer
from core.services.phone import PhoneNumberService


class PhoneViewSet(PreventDeletionOfMainAttributeMixin, SetMainAttributeMixin, ModelViewSet):
    """
    Methods to manipulate with `Address` entity.
    """

    serializer_class = PhoneSerializer
    main_attribute = "main_phone"

    def perform_create(self, serializer):
        phone_service = PhoneNumberService(serializer)
        serializer = phone_service.cleanup_phone_number()

        super().perform_create(serializer)

    def perform_update(self, serializer):
        phone_service = PhoneNumberService(serializer)
        serializer = phone_service.cleanup_phone_number()

        super().perform_update(serializer)

    def get_queryset(self):
        client = self.request.user.client
        return client.phone_list.all()
