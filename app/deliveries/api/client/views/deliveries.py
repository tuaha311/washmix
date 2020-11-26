from rest_framework.viewsets import ModelViewSet

from api.permissions import default_driver_permissions
from deliveries.api.client.serializers.deliveries import DeliverySerializer


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = default_driver_permissions

    def get_queryset(self):
        employee = self.request.user.employee
        return employee.delivery_list.all()
