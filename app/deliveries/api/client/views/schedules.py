from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from deliveries.api.client.serializers.schedule import ScheduleSerializer
from deliveries.models import Schedule


class ScheduleViewSet(ModelViewSet):
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        client = self.request.user.client
        return client.schedule_list.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = self.request.user.client
        if Schedule.objects.filter(client=client).exists():
            return Response(
                {"message": "You can not create multiple schedules"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        serializer.save(client=client)
