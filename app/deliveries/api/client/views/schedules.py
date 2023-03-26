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
        Log.objects.create(customer=self.request.user.email, action="Created Recurring Pickup")
        send_admin_client_information(
            self.request.user.client.id,
            f"The user Created New Recurring Pickup",
            "Customer Account Update",
        )

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        Log.objects.create(customer=self.request.user.email, action="Deleted Recurring Pickup")
        send_admin_client_information(
            self.request.user.client.id,
            f"The user deleted Recurring Pickup",
            "Customer Account Update",
        )

    def perform_update(self, serializer):
        old_days = Schedule.objects.get(client=self.request.user.client).days
        super().perform_update(serializer)
        new_days = Schedule.objects.get(client=self.request.user.client).days

        if old_days != new_days:
            Log.objects.create(customer=self.request.user.email, action="Updated Recurring Pickup")
            send_admin_client_information(
                self.request.user.client.id,
                f"The user updated Recurring Pickup",
                "Customer Account Update",
            )
