from rest_framework.viewsets import ModelViewSet

from deliveries.v1.serializers.deliveries import DeliverySerializer


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer

    def get_queryset(self):
        employee = self.request.user.employee
        return employee.delivery_list.all()
