from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated


class BaseAttributePermission(BasePermission):
    attribute_name = ""

    def has_permission(self, request, view):
        user = request.user

        client = getattr(user, self.attribute_name, None)

        return bool(client)


class IsClient(BaseAttributePermission):
    message = "API endpoint only for clients."
    attribute_name = "client"


class IsEmployee(BaseAttributePermission):
    message = "Employees only API endpoint."
    attribute_name = "employee"


default_driver_permissions = [IsAuthenticated, IsEmployee]
default_pos_permissions = [IsAuthenticated, IsEmployee, IsAdminUser]
