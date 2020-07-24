from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from swap_user.models.email import EmailUser

from core.common_models import Common
from modules.enums import AppUsers, Crease, Detergents, SignUp, Starch
from users.base_models import AbstractEmployee


class Employee(AbstractEmployee):
    """
    Employees of laundry who processing orders or
    who delivers orders to clients.
    """

    LAUNDRESS = "laundress"
    DRIVER = "driver"
    MANAGER = "manager"
    POSITION_MAP = {
        DRIVER: "Driver",
        LAUNDRESS: "Laundress",
        MANAGER: "Manager",
    }
    POSITION_CHOICES = list(POSITION_MAP.items())

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee",
    )
    position = models.CharField(
        verbose_name="position of employee",
        max_length=20,
        default=LAUNDRESS,
        choices=POSITION_CHOICES,
    )

    class Meta:
        verbose_name = "employee"
        verbose_name_plural = "employees"


class Client(Common):
    """
    Online-only clients of application. They used our application to
    make orders and request pickups.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client",
    )
    package = models.ForeignKey(
        "core.Package",
        verbose_name="package of service",
        related_name="client_list",
        on_delete=models.CASCADE,
        null=True,
    )
    main_phone = models.OneToOneField(
        "core.Phone",
        verbose_name="phone number",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
    )
    main_address = models.OneToOneField(
        "core.Address",
        verbose_name="user",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
    )

    # Customer information
    is_doormen = models.BooleanField(
        default=False,
    )
    stripe_customer_id = models.TextField(
        null=True,
    )
    balance = models.FloatField(
        default=0,
    )

    # Preferences
    detergents = models.CharField(
        max_length=50,
        choices=[(item, item.value) for item in Detergents],
        null=True,
    )
    starch = models.CharField(
        max_length=50,
        choices=[(item, item.value) for item in Starch],
        null=True,
    )
    no_crease = models.CharField(
        max_length=50,
        choices=[(item, item.value) for item in Crease],
        null=True,
    )
    app_users = models.CharField(
        max_length=30,
        choices=[(item, item.value) for item in AppUsers],
        null=True,
        default=AppUsers.REGULAR_USERS.value,
    )
    authentication_provider = models.CharField(
        max_length=30,
        choices=[(item, item.value) for item in SignUp],
        null=True,
        default=SignUp.washmix.value,
    )

    fabric_softener = models.BooleanField(
        default=False,
    )
    fix_tears = models.BooleanField(
        default=False,
    )
    is_coupon = models.BooleanField(
        default=False,
    )
