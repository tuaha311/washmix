from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from pickups.serializers import DeliverySerializer


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.delivery_list.all()

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        return serializer.save(client=client)
