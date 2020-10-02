from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from pickups.serializers.schedule import ScheduleSerializer


class ScheduleViewSet(ModelViewSet):
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.schedule_list.all()

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        serializer.save(client=client)
