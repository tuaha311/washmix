from datetime import date, time
from typing import Optional, Tuple

from django.db.transaction import atomic
from django.utils.timezone import localtime
from orders.choices import OrderPaymentChoices

from billing.models import Invoice
from billing.services.invoice import InvoiceService
from core.interfaces import PaymentInterfaceService
from deliveries.choices import DeliveryKind, DeliveryStatus
from deliveries.containers.request import RequestContainer
from deliveries.models import Delivery, Request
from deliveries.utils import get_dropoff_day, get_pickup_day, get_pickup_start_end
from deliveries.validators import RequestValidator
from notifications.models import Notification, NotificationTypes
from notifications.tasks import send_admin_client_information
from orders.containers.basket import BasketContainer
from orders.models import Basket, Order
from subscriptions.models import Subscription
from users.models import Client, Log


class RequestService(PaymentInterfaceService):
    """
    This service is responsible for Requests / Deliveries handling.

    Order of methods by importance:
        - refresh_amount_with_discount
        - charge
    """

    def __init__(
        self,
        client: Client,
        pickup_date: date = None,
        pickup_start: time = None,
        pickup_end: time = None,
        is_rush: bool = False,
    ):
        self._client = client

        if pickup_date is None:
            pickup_date = self._pickup_day_auto_complete

        if pickup_start is None or pickup_end is None:
            pickup_start, pickup_end = self._pickup_start_end_auto_complete

        self._pickup_date = pickup_date
        self._pickup_start = pickup_start
        self._pickup_end = pickup_end
        self._is_rush = is_rush
        self._validator_service = RequestValidator(pickup_date, pickup_start, pickup_end, zip_code = client.main_address.zip_code, client=client)

    def refresh_amount_with_discount(
        self,
        order: Order,
        basket: Optional[Basket],
        request: Optional[Request],
        subscription: Optional[Subscription],
        **kwargs,
    ) -> Optional[float]:
        """
        Invoicing method, called when POS checkout occurs.
        Creates 2 invoice - for Pickup Delivery and for Dropoff Delivery.
        """

        if not basket or not request:
            return None

        client = self._client
        subscription = client.subscription
        invoice_service = InvoiceService(client)
        basket_container = BasketContainer(subscription, basket)  # type: ignore
        request_container = RequestContainer(subscription, request, basket_container)  # type: ignore
        amount = request_container.amount + request_container.rush_amount
        discount = request_container.discount

        request = invoice_service.refresh_amount_discount(
            entity=request,
            amount=amount,
            discount=discount,
        )

        return request.amount_with_discount

    def confirm(
        self,
        request: Optional[Request],
        basket: Optional[Basket],
        subscription: Optional[Subscription],
        invoice: Invoice,
        **kwargs,
    ):
        pass

    def checkout(self, **kwargs):
        """
        Dummy implementation of interface.
        """
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
                kind=DeliveryKind.PICKUP,
                status=DeliveryStatus.ACCEPTED,
                **pickup_info,
            )
            Delivery.objects.create(
                request=request,
                kind=DeliveryKind.DROPOFF,
                status=DeliveryStatus.ACCEPTED,
                **dropoff_info,
            )

            send_admin_client_information(
                self._client.id,
                "A New Pickup Request is Created",
                is_pickup=True,
                pickup_date=pickup_info.get("date").strftime("%B %d, %Y"),
            )
            Log.objects.create(customer=self._client.email, action="Created New Pick Up Request")
            Notification.create_notification(self._client, NotificationTypes.NEW_PICKUP_REQUEST)
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
                kind=DeliveryKind.PICKUP,
                status=DeliveryStatus.ACCEPTED,
                defaults=pickup_info,
            )
            Delivery.objects.get_or_create(
                request=request,
                kind=DeliveryKind.DROPOFF,
                status=DeliveryStatus.ACCEPTED,
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

    @property
    def _pickup_start_end_auto_complete(self) -> Tuple[time, time]:
        now = localtime()
        return get_pickup_start_end(now)

    @property
    def _pickup_day_auto_complete(self) -> date:
        now = localtime()
        return get_pickup_day(now, self._client)

    @property
    def _dropoff_info(self) -> dict:
        """
        Usually, we processing order 2 days and delivering on the next day - i.e.
        3 business days.
        """

        pickup_date = self._pickup_date
        pickup_start = self._pickup_start
        pickup_end = self._pickup_end
        is_rush = self._is_rush

        dropoff_date = get_dropoff_day(pickup_date, is_rush, client=self._client)

        return {
            "date": dropoff_date,
            "start": pickup_start,
            "end": pickup_end,
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


class AdminRequestService(RequestService):
    """
    This service is responsible for Admin Requests handling.
    """
    
    def create(self, **extra_kwargs) -> Request:
        """
        Create a new Admin Request.
        """

        self._validator_service.validate()

        dropoff_info = self._dropoff_info
        pickup_info = self._pickup_info

        address = self._client.main_address
        extra_kwargs.setdefault("address", address)
        extra_kwargs.setdefault("is_rush", False)

        with atomic():
            # Add a check and find the request that was created by Admin and it either does not have the order or it's not been charged.
            existed_request = Request.objects.filter(client=self._client, order__payment=OrderPaymentChoices.UNPAID, generated_by_admin=True).first()

            if existed_request:
                request = existed_request

            else:
                request = Request.objects.create(
                client=self._client,
                comment="This request was initiated by an admin",
                generated_by_admin=True,
                **extra_kwargs,
                )
                Delivery.objects.create(
                    request=request,
                    kind=DeliveryKind.PICKUP,
                    status=DeliveryStatus.COMPLETED,
                    **pickup_info,
                )
                Delivery.objects.create(
                    request=request,
                    kind=DeliveryKind.DROPOFF,
                    status=DeliveryStatus.COMPLETED,
                    **dropoff_info,
                )

            send_admin_client_information(
                self._client.id,
                "A New Admin Request is Created",
            )
            Log.objects.create(customer=self._client.email, action="Created new Admin Request to charge customer.")
            # Notification.create_notification(self._client, NotificationTypes.NEW_ADMIN_REQUEST)

        return request