from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework.schemas.openapi import SchemaGenerator


class WashMixSchemaGenerator(OpenAPISchemaGenerator):
    """
    Provide custom schema generator with overloaded permissions.
    We are allow browsing without authentication for OpenAPI docs.
    """

    def has_view_permissions(self, path, method, view):
        return True
