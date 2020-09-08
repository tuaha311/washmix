from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from pickups.serializers.deliveries import DeliverySerializer
from pickups.services.delivery import calculate_dropoff


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.delivery_list.all()

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        pickup_date = serializer.validated_data["pickup_date"]

        dropoff = calculate_dropoff(pickup_date)

        return serializer.save(client=client, **dropoff)
