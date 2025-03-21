from drf_yasg.inspectors import SwaggerAutoSchema


class WashMixAutoSchema(SwaggerAutoSchema):
    """
    Custom view inspector that provides a neat feature -
    you can explicitly define response object in OpenAPI schema via
    DRF serializer.

    Just define `response_serializer_class` attribute on view - it's all.
    """

    response_serializer_attribute = "response_serializer_class"
    empty_response_attribute = "empty_response"
    is_list_response_attribute = "is_list_response"

    def get_default_response_serializer(self):
        """
        Method allows us to set a different response schema via serializer if
        defined `response_serializer_class` attribute.
        """

        serializer = super().get_default_response_serializer()

        if hasattr(self.view, self.response_serializer_attribute):
            serializer_class = getattr(self.view, self.response_serializer_attribute)
            serializer = serializer_class()

        return serializer

    def get_response_schemas(self, response_serializers):
        """
        Method removes `schema` fields from OpenAPI spec if
        `empty_response` attribute set on view.
        """

        responses = super().get_response_schemas(response_serializers)

        if hasattr(self.view, self.empty_response_attribute):
            for value in responses.values():
                value.pop("schema")

        return responses

    def has_list_response(self):
        """
        Method allows to us control `responses` field - we can return `array` or
        `schema` fields.
        """

        has_list_response = super().has_list_response()

        if hasattr(self.view, self.is_list_response_attribute):
            is_list_response = getattr(self.view, self.is_list_response_attribute)
            return is_list_response

        return has_list_response
