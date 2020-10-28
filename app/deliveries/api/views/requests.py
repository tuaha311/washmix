from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from deliveries.api.serializers.requests import RequestSerializer
from deliveries.services.requests import RequestService


class RequestViewSet(ModelViewSet):
    serializer_class = RequestSerializer
    recalculate_fields = {"pickup_date"}

    def get_queryset(self):
        client = self.request.user.client
        return client.request_list.all()

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        pickup_date = serializer.validated_data["pickup_date"]
        address = serializer.validated_data["address"]

        service = RequestService(client=client, pickup_date=pickup_date,)
        request = service.create(address=address)

        serializer.instance = request

    def perform_update(self, serializer):
        update_fields = set(serializer.validated_data.keys())
        client = self.request.user.client

        if self.recalculate_fields & update_fields:
            pickup_date = serializer.validated_data["pickup_date"]
            request = serializer.instance

            service = RequestService(
                client=client,
                pickup_date=pickup_date,
                pickup_start=request.pickup_start,
                pickup_end=request.pickup_end,
            )
            service.recalculate(request)

        serializer.save()
