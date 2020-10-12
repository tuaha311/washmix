from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from deliveries.services.delivery import DeliveryService
from deliveries.v1.serializers.deliveries import DeliverySerializer


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.delivery_list.all()

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        pickup_date = serializer.validated_data["pickup_date"]
        address = serializer.validated_data["address"]

        service = DeliveryService(client=client, address=address, pickup_date=pickup_date,)
        delivery = service.create()

        serializer.instance = delivery
