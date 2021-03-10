from django.db.transaction import atomic

from rest_framework.serializers import Serializer, ValidationError

from users.models import Client


class MainAttributeService:
    def __init__(self, client: Client, main_attribute: str):
        self._main_attribute = main_attribute
        self._client = client

    def create(self, serializer: Serializer):
        main_attribute = self._main_attribute

        with atomic():
            instance = serializer.save(client=self._client)
            main_attribute_value = getattr(self._client, main_attribute)

            if not main_attribute_value:
                setattr(self._client, main_attribute, instance)
                self._client.save(update_fields={main_attribute})

        return instance

    def delete(self, instance):
        main_attribute_value = getattr(self._client, self._main_attribute)

        if main_attribute_value == instance:
            raise ValidationError(
                detail=f"You can't remove {self._main_attribute}.",
                code=f"{self._main_attribute}_cant_be_removed",
            )

        instance.delete()
