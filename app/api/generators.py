from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework.permissions import IsAuthenticated


class WashMixSchemaGenerator(OpenAPISchemaGenerator):
    """
    Provide custom schema generator that adds
    custom `security` fields into OpenAPI schema.
    """

    def get_operation(self, view, path, prefix, method, components, request):
        operation = super().get_operation(view, path, prefix, method, components, request)

        if IsAuthenticated in view.permission_classes:
            operation.security = ["Bearer"]

        return operation
