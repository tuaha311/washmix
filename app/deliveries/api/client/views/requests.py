from django_filters import rest_framework as filters
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from deliveries.api.client.serializers.requests import RequestCheckSerializer, RequestSerializer
from deliveries.services.requests import RequestService
from orders.choices import StatusChoices


class RequestFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(field_name="order__status", choices=StatusChoices.CHOICES)
    created = filters.DateTimeFilter(field_name="created", lookup_expr="gte")

    class Meta:
        fields = [
            "status",
            "created",
        ]


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

        service = RequestService(
            client=client,
            pickup_date=pickup_date,
        )
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


class RequestCheckView(GenericAPIView):
    """
    Goal of this view - validate request pickup date and time.
    """

    serializer_class = RequestCheckSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return Response()
