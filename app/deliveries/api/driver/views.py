from django.conf import settings
from django.utils.timezone import localtime

from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import default_driver_permissions
from deliveries.api.driver.serializers import DeliverySerializer
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.utils import update_deliveries_to_no_show


class DeliveryViewSet(ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = default_driver_permissions
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = (
        "kind",
        "status",
    )

    def get_queryset(self):
        now = localtime()
        employee = self.request.user.employee

        one_week_ago = now - settings.FULL_WEEK_DURATION_TIMEDELTA
        delivery_list = employee.delivery_list.filter(date__gte=one_week_ago)

        return delivery_list

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            status = request.data["status"]
        except:
            status = None

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if instance.kind == DeliveryKind.PICKUP and status == DeliveryStatus.NO_SHOW:
            print("Marking the Delivery to No Show and Charging client.")
            update_deliveries_to_no_show(instance)

        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
