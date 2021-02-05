from django.db.models import Q
from django.utils.timezone import localtime

from django_filters import rest_framework as filters
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from deliveries.api.client.serializers.requests import RequestCheckSerializer, RequestSerializer
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.services.requests import RequestService
from orders.choices import OrderStatusChoices


class RequestFilter(filters.FilterSet):
    is_upcoming = filters.BooleanFilter(method="filter_upcoming")

    class Meta:
        fields = [
            "is_upcoming",
        ]

    def filter_upcoming(self, queryset, name, value):
        request_list = queryset
        today = localtime().date()

        if not value:
            return request_list

        # we are preparing conditions by orders:
        #   - find requests with accepted or in progress orders
        #   - find requests without order
        without_orders = Q(order__isnull=True)
        without_completed_orders = Q(
            order__status__in=[OrderStatusChoices.ACCEPTED, OrderStatusChoices.IN_PROGRESS]
        )
        order_query = without_orders | without_completed_orders

        # conditions by dropoffs:
        #   - find requests with dropoffs, that have a date greater or equal to today
        #   - find requests with deliveries, that are accepted or in progress
        without_expired_deliveries = Q(
            delivery_list__kind=DeliveryKind.DROPOFF, delivery_list__date__gte=today
        )
        without_completed_deliveries = Q(
            delivery_list__status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.IN_PROGRESS]
        )
        dropoff_query = without_expired_deliveries & without_completed_deliveries
        filtered_result = request_list.filter(order_query & dropoff_query).distinct()

        return filtered_result


class RequestViewSet(ModelViewSet):
    serializer_class = RequestSerializer
    recalculate_fields = {"pickup_date"}
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter

    def get_queryset(self):
        client = self.request.user.client
        return client.request_list.all()

    def perform_create(self, serializer: Serializer):
        client = self.request.user.client
        pickup_date = serializer.validated_data["pickup_date"]
        address = serializer.validated_data["address"]
        is_rush = serializer.validated_data.get("is_rush", False)
        instructions = address.instructions

        service = RequestService(
            client=client,
            pickup_date=pickup_date,
            is_rush=is_rush,
        )
        request = service.create(address=address, comment=instructions)

        serializer.instance = request

    def perform_update(self, serializer: Serializer):
        update_fields = set(serializer.validated_data.keys())
        client = self.request.user.client

        if self.recalculate_fields & update_fields:
            pickup_date = serializer.validated_data["pickup_date"]
            request = serializer.instance
            pickup_start = request.pickup_start
            pickup_end = request.pickup_end
            is_rush = request.is_rush

            service = RequestService(
                client=client,
                pickup_date=pickup_date,
                pickup_start=pickup_start,
                pickup_end=pickup_end,
                is_rush=is_rush,
            )
            service.recalculate(request)

        serializer.save()


class RequestCheckView(GenericAPIView):
    """
    Goal of this view - validate request pickup date and time.
    """

    serializer_class = RequestCheckSerializer

    def post(self, request: DRFRequest, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return Response()
