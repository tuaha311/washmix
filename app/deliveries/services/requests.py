from datetime import date, time
from typing import Tuple

from django.conf import settings
from django.db.transaction import atomic
from django.utils.timezone import localtime

from deliveries.choices import Kind, Status
from deliveries.models import Delivery, Request
from deliveries.utils import get_dropoff_day, get_pickup_day, get_pickup_start_end
from deliveries.validators import RequestValidator
from notifications.tasks import send_email
from orders.containers.order import OrderContainer
from orders.services.basket import BasketService
from orders.services.order import OrderService
from users.models import Client


class RequestService:
    def __init__(
        self,
        client: Client,
        pickup_date: date = None,
        pickup_start: time = None,
        pickup_end: time = None,
    ):
        self._client = client

        if pickup_date is None:
            pickup_date = self._pickup_day_auto_complete

        if pickup_start is None or pickup_end is None:
            pickup_start, pickup_end = self._pickup_start_end_auto_complete

        self._pickup_date = pickup_date
        self._pickup_start = pickup_start
        self._pickup_end = pickup_end
        self._validator_service = RequestValidator(pickup_date, pickup_start, pickup_end)

    def choose(self, request: Request) -> OrderContainer:
        with atomic():
            order_service = self._get_order_service()
            order = order_service.order
            basket = order.basket

            order.request = request
            order.save()

            order_service.create_delivery_invoice(order, basket, request)

        return order_service.get_container()

    def create(self, **extra_kwargs) -> Request:
        """
        Like default manager's `create` method but with some changes:
            - Added extra validation on date, time, etc.
            - Added auto completion of dropoff info.
        """

        self._validator_service.validate()

        dropoff_info = self._dropoff_info
        pickup_info = self._pickup_info

        address = self._client.main_address
        extra_kwargs.setdefault("address", address)
        extra_kwargs.setdefault("is_rush", False)

        with atomic():
            request = Request.objects.create(
                client=self._client,
                **extra_kwargs,
            )
            Delivery.objects.create(
                request=request,
                kind=Kind.PICKUP,
                status=Status.ACCEPTED,
                **pickup_info,
            )
            Delivery.objects.create(
                request=request,
                kind=Kind.DROPOFF,
                status=Status.ACCEPTED,
                **dropoff_info,
            )

        self._notify_client_on_new_request()

        return request

    def get_or_create(self, extra_query: dict, extra_defaults: dict) -> Tuple[Request, bool]:
        """
        Like default manager's `update_or_create` method but with some changes:
            - Added extra validation on date, time, etc.
            - Added auto completion of dropoff info.
        """

        self._validator_service.validate()

        dropoff_info = self._dropoff_info
        pickup_info = self._pickup_info

        address = self._client.main_address
        extra_defaults.setdefault("address", address)
        extra_defaults.setdefault("is_rush", False)

        with atomic():
            request, created = Request.objects.get_or_create(
                client=self._client,
                **extra_query,
                defaults=extra_defaults,
            )
            Delivery.objects.get_or_create(
                request=request,
                kind=Kind.PICKUP,
                status=Status.ACCEPTED,
                defaults=pickup_info,
            )
            Delivery.objects.get_or_create(
                request=request,
                kind=Kind.DROPOFF,
                status=Status.ACCEPTED,
                defaults=dropoff_info,
            )

        return request, created

    def recalculate(self, request: Request) -> Request:
        """
        This method helps to recalculate dropoff info on update
        field `pickup_date`.
        """

        dropoff_info = self._dropoff_info
        dropoff = request.dropoff

        for key, value in dropoff_info.items():
            setattr(dropoff, key, value)
        dropoff.save()

        return request

    def validate(self):
        self._validator_service.validate()

    def _notify_client_on_new_request(self):
        client_id = self._client.id

        send_email.send(
            client_id=client_id,
            event=settings.NEW_REQUEST,
        )

    def _get_order_service(self) -> OrderService:
        client = self._client
        basket_service = BasketService(client)

        order_service = basket_service.get_order_service()

        return order_service

    @property
    def _pickup_start_end_auto_complete(self) -> Tuple[time, time]:
        now = localtime()
        return get_pickup_start_end(now)

    @property
    def _pickup_day_auto_complete(self) -> date:
        now = localtime()
        return get_pickup_day(now)

    @property
    def _dropoff_info(self) -> dict:
        """
        Usually, we processing order 2 days and delivering on the next day - i.e.
        3 business days.
        """

        dropoff_date = get_dropoff_day(self._pickup_date)

        return {
            "date": dropoff_date,
            "start": self._pickup_start,
            "end": self._pickup_end,
        }

    @property
    def _pickup_info(self) -> dict:
        """
        Usually, we processing order 2 days and delivering on the next day - i.e.
        3 business days.
        """

        return {
            "date": self._pickup_date,
            "start": self._pickup_start,
            "end": self._pickup_end,
        }
