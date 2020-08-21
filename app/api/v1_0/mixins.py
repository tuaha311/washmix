from django.db.transaction import atomic

from rest_framework.request import Request


class MainAttributeMixin:
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
