from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from pickups.serializers.deliveries import DeliverySerializer
from pickups.services.delivery import DeliveryService


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.delivery_list.all()

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        pickup_date = serializer.validated_data["pickup_date"]
        pickup_start = serializer.validated_data["pickup_start"]
        pickup_end = serializer.validated_data["pickup_end"]

        service = DeliveryService(
            pickup_date=pickup_date, pickup_start=pickup_start, pickup_end=pickup_end,
        )
        dropoff_kwargs = service.dropoff

        return serializer.save(client=client, **dropoff_kwargs)
