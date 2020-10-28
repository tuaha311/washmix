from rest_framework.viewsets import ModelViewSet

from api.permissions import default_permissions_for_employee
from deliveries.v1.serializers.deliveries import DeliverySerializer


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = default_permissions_for_employee

    def get_queryset(self):
        employee = self.request.user.employee
        return employee.delivery_list.all()
