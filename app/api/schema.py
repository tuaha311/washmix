from rest_framework.schemas.openapi import AutoSchema


class WashMixAutoSchema(AutoSchema):
    """
    Adds `type` attribute for OpenAPI schema.
    """

    def _map_serializer(self, serializer):
        result = super()._map_serializer(serializer)
        result["type"] = "object"

        return result
