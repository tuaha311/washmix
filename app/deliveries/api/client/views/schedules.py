from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from deliveries.api.client.serializers.schedule import ScheduleSerializer
from deliveries.models import Schedule
from notifications.tasks import send_admin_client_information
from users.models import Log


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

    def perform_update(self, serializer):
        super().perform_update(serializer)
        Log.objects.create(customer=self.request.user.email, action="Updated Preferences")
        send_admin_client_information(self.request.user.client.id, f"The user updated preferences")
