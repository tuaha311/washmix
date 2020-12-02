from datetime import date, time
from typing import List, Optional, Tuple

from django.conf import settings
from django.db.transaction import atomic
from django.utils.timezone import localtime

from billing.models import Invoice
from billing.services.invoice import InvoiceService
from deliveries.choices import Kind, Status
from deliveries.containers.request import RequestContainer
from deliveries.models import Delivery, Request
from deliveries.utils import get_dropoff_day, get_pickup_day, get_pickup_start_end
from deliveries.validators import RequestValidator
from notifications.tasks import send_email
from orders.containers.basket import BasketContainer
from orders.models import Basket, Order
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

    def create_invoice(
        self,
        order: Order,
        basket: Optional[Basket],
        request: Optional[Request],
        **kwargs,
    ) -> Optional[List[Invoice]]:
        """
        Invoicing method, called when POS checkout occurs.
        Creates 2 invoice - for Pickup Delivery and for Dropoff Delivery.
        """

        if not basket or not request:
            return None

        client = self._client
        subscription = client.subscription
        invoice_service = InvoiceService(client)
        basket_container = BasketContainer(subscription, basket)
        request_container = RequestContainer(subscription, request, basket_container)

        # we have 2 kind - Pickup, Dropoff
        # and for every of Delivery we create an invoice
        kind_of_deliveries = Kind.MAP.keys()
        invoice_list = []

        for kind in kind_of_deliveries:
            delivery_container_name = f"{kind}_container"
            delivery_container = getattr(request_container, delivery_container_name)

            delivery_invoice = invoice_service.update_or_create(
                order=order,
                amount=delivery_container.amount,
                discount=delivery_container.discount,
                purpose=kind,
            )

            invoice_attribute_name = f"{kind}_invoice"
            setattr(request, invoice_attribute_name, delivery_invoice)

            invoice_list.append(delivery_invoice)

        request.save()

        return invoice_list

    def charge(self, request: Request, **kwargs):
        pass

    def validate(self):
        """
        Makes all validation stuff.
        """

        self._validator_service.validate()

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

    def _notify_client_on_new_request(self):
        client_id = self._client.id
        recipient_list = [self._client.email]

        send_email.send(
            event=settings.NEW_REQUEST,
            recipient_list=recipient_list,
            extra_context={
                "client_id": client_id,
            },
        )

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
