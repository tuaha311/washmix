from django.conf import settings
from django.utils.timezone import localtime

from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet

from api.permissions import default_driver_permissions
from deliveries.api.driver.serializers import DeliverySerializer


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
