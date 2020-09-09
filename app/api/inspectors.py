from drf_yasg.inspectors import SwaggerAutoSchema


class WashMixAutoSchema(SwaggerAutoSchema):
    """
    Custom view inspector that provides a neat feature -
    you can explicitly define response object in OpenAPI schema via
    DRF serializer.

    Just define `response_serializer_class` attribute on view - it's all.
    """

    response_serializer_attribute = "response_serializer_class"

    def get_default_response_serializer(self):
        serializer = super().get_default_response_serializer()

        if hasattr(self.view, self.response_serializer_attribute):
            serializer_class = getattr(self.view, self.response_serializer_attribute)
            serializer = serializer_class()

        return serializer
