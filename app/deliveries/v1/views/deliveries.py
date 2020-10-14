from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from deliveries.services.delivery import DeliveryService
from deliveries.v1.serializers.deliveries import DeliverySerializer


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer
    recalculate_fields = {"pickup_date"}

    def get_queryset(self):
        client = self.request.user.client
        return client.delivery_list.all()

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        pickup_date = serializer.validated_data["pickup_date"]
        address = serializer.validated_data["address"]

        service = DeliveryService(client=client, pickup_date=pickup_date,)
        delivery = service.create(address=address)

        serializer.instance = delivery

    def perform_update(self, serializer):
        update_fields = set(serializer.validated_data.keys())
        client = self.request.user.client

        if self.recalculate_fields & update_fields:
            pickup_date = serializer.validated_data["pickup_date"]
            delivery = serializer.instance

            service = DeliveryService(
                client=client,
                pickup_date=pickup_date,
                pickup_start=delivery.pickup_start,
                pickup_end=delivery.pickup_end,
            )
            service.recalculate(delivery)

        serializer.save()
