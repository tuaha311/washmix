from rest_framework.request import Request

from core.services.main_attribute import MainAttributeService


class SetMainAttributeMixin:
    """
    Convenient mixin to create linked instance with client
    if client doesn't have `main_attribute`.

    Mostly used in AddressViewSet, PhoneViewSet, CardViewSet.
    """

    request: Request
    main_attribute: str

    def perform_create(self, serializer):
        service = MainAttributeService(self.request.user.client, self.main_attribute)

        instance = service.create(serializer)

        return instance


class PreventDeletionOfMainAttributeMixin:
    """
    We can't validate request body of DELETE method and because of it
    we should validate instance at view level.

    Also, we prevent deletion of main attribute - because it will lead
    us to the situation where we have't enough data for orders.
    """

    request: Request
    main_attribute: str

    def perform_destroy(self, instance):
        service = MainAttributeService(self.request.user.client, self.main_attribute)

        service.delete(instance)
