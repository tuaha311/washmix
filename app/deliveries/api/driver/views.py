from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet

from api.permissions import default_driver_permissions
from deliveries.api.driver.serializers import DeliverySerializer


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = default_driver_permissions
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("kind",)

    def get_queryset(self):
        employee = self.request.user.employee
        return employee.delivery_list.all()
