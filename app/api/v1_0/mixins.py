from django.db.transaction import atomic

from rest_framework.request import Request
from rest_framework.serializers import ValidationError


class SetMainAttributeMixin:
    """
    Convenient mixin to create linked instance with client
    if client doesn't have `main_attribute`.

    Mostly used in AddressViewSet, PhoneViewSet, CardViewSet.
    """

    request: Request
    main_attribute: str

    def perform_create(self, serializer):
        client = self.request.user.client

        with atomic():
            instance = serializer.save(client=client)
            main_attribute_value = getattr(client, self.main_attribute)

            if not main_attribute_value:
                setattr(client, self.main_attribute, instance)
                client.save()

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
        client = self.request.user.client
        main_attribute_value = getattr(client, self.main_attribute)

        if main_attribute_value == instance:
            raise ValidationError(
                detail=f"You can't remove {self.main_attribute}.",
                code=f"{self.main_attribute}_cant_be_removed",
            )

        instance.delete()
