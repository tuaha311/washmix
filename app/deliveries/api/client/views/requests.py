import datetime

from django.conf import settings
from django.db.models import Q, QuerySet
from django.utils import timezone

from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from deliveries.api.client.serializers.requests import ChargeCustomerSerializer, RequestCheckSerializer, RequestSerializer
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.models import Delivery
from deliveries.services.requests import AdminRequestService, RequestService
from notifications.models import Notification, NotificationTypes
from notifications.tasks import send_admin_client_information, send_sms
from orders.choices import OrderStatusChoices
from settings.base import ALLOW_DELIVERY_CANCELLATION_TIMEDELTA, ALLOW_DELIVERY_RESHEDULE_TIMEDELTA
from users.models import Log, Client
from rest_framework.permissions import AllowAny


class RequestFilter(filters.FilterSet):
    is_upcoming = filters.BooleanFilter(method="filter_upcoming")

    class Meta:
        fields = [
            "is_upcoming",
        ]

    def filter_upcoming(self, queryset: QuerySet, name: str, value: bool):
        request_list = queryset
        today = timezone.localtime().date()

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
        without_no_show = Q(
            delivery_list__kind=DeliveryKind.PICKUP, delivery_list__status=DeliveryStatus.NO_SHOW
        )
        dropoff_query = without_expired_deliveries & without_completed_deliveries
        filtered_result = request_list.filter(order_query & dropoff_query).distinct()
        filtered_again = filtered_result.exclude(without_no_show).distinct()

        return filtered_again


class RequestViewSet(ModelViewSet):
    serializer_class = RequestSerializer
    recalculate_fields = {"pickup_date"}
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilter

    def get_queryset(self):
        client = self.request.user.client
        return client.request_list.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = self.request.user.client
        if Delivery.objects.filter(
            request__client=client,
            status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.IN_PROGRESS],
            kind=DeliveryKind.PICKUP,
        ).exists():
            pickup = Delivery.objects.filter(
                request__client=client,
                status__in=[DeliveryStatus.ACCEPTED, DeliveryStatus.IN_PROGRESS],
                kind=DeliveryKind.PICKUP,
            )[0]
            pickup_date = pickup.date

            number = client.main_phone.number
            send_sms.send_with_options(
                kwargs={
                    "event": settings.UNABLE_TO_CREATE_MULTIPLE_REQUEST,
                    "recipient_list": [number],
                    "extra_context": {
                        "date_pickup": pickup_date.strftime("%B %d, %Y"),
                        "day_pickup": pickup_date.strftime("%A"),
                    },
                },
                delay=settings.DRAMATIQ_DELAY_FOR_DELIVERY,
            )
            return Response(
                {"non_field_errors": ["You already have a pickup request made"]},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
        request = service.create(address=address, comment=instructions, is_rush=is_rush)
        pretty_date = pickup_date.strftime("%B %d, %Y")

        serializer.instance = request

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        request = serializer.instance
        if request.created + ALLOW_DELIVERY_RESHEDULE_TIMEDELTA < timezone.now():
            message = "Sorry, but your pickup is already scheduled and it’s passed our cutoff time to make any changes. If any questions email cs@washmix.com or text 415-993-9274"

            return Response(
                {"message": message},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        Log.objects.create(customer=self.request.user.email, action="Updated Pick Up Request")

        return Response(serializer.data)

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
        pretty_date = pickup_date.strftime("%B %d, %Y")

        send_admin_client_information(
            client.id,
            "A Customer has Updated their Pickup Request.",
            is_pickup=True,
            pickup_date=pretty_date,
        )

        Notification.create_notification(
            client, NotificationTypes.PICKUP_DATE_CHANGE, description=f"to {pretty_date}"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        time_now = timezone.now()
        created_at = instance.created
        client = request.user.client

        if time_now > created_at + ALLOW_DELIVERY_CANCELLATION_TIMEDELTA:
            return Response(
                {
                    "message": "We have already scheduled this pickup - unfortunately, it’s now too late to cancel this request. Please email cs@washmix.com"
                },
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        deliveries = Delivery.objects.filter(request=instance.pk)

        for delivery in deliveries:
            delivery.status = DeliveryStatus.CANCELLED
            delivery.save()

        if deliveries:
            send_admin_client_information(client.id, "A Customer has Canceled the Pickup Request")
            Log.objects.create(customer=client.email, action="Cancelled Pick Up Request")

        Notification.create_notification(client, NotificationTypes.PICKUP_REQUEST_CANCELED)
        return Response({"message": "request canceled"}, status=status.HTTP_200_OK)


class RequestCheckView(GenericAPIView):
    """
    Goal of this view - validate request pickup date and time.
    """

    serializer_class = RequestCheckSerializer

    def post(self, request: DRFRequest, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return Response()

class ChargeCustomerViewSet(ModelViewSet):
    serializer_class = ChargeCustomerSerializer
    authentication_classes = []  # Remove all authentication classes
    permission_classes = [AllowAny]

    def create(self, request):

        # Deserialize the request data using the serializer
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get customer ID and other charging parameters from the serializer
        client_id = serializer.validated_data["client_id"]
        order_items = serializer.validated_data.get("order_items")
        amount = serializer.validated_data.get("amount")
        waive_delivery_charge = serializer.validated_data.get("waive_delivery_charge")
        rush_service_charge = serializer.validated_data.get("rush_service_charge")

        # Get the customer object
        try:
            client = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            return Response(
                {"error": "Client with the specified ID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Perform the charging logic here based on the provided parameters
        # You can use the information provided to charge the customer accordingly
        # For example, apply charges to specific order items or the entire order
        request_obj = self.perform_create(serializer, client)

        # If the charging is successful, construct the URL with client_id and request_id
        response_data = {
            "message": "Client charged successfully.",
            "path": f"/admin/pos/?client_id={client_id}&request_id={request_obj.id}&is_admin=1",
            "status": status.HTTP_200_OK
        }

        return Response(response_data)

    def perform_create(self, serializer: Serializer, client):
        is_rush = serializer.validated_data.get("is_rush", False)
        service = AdminRequestService(
            client=client,
            is_rush=is_rush,
        )
        request = service.create(is_rush=is_rush)

        return request
