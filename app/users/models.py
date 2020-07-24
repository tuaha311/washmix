from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

from swap_user.models.email import EmailUser

from core.common_models import Common
from modules.enums import AppUsers, Crease, Detergents, SignUp, Starch


class Employee(Common):
    """
    Employee of laundry who processing orders
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee",
    )

    class Meta:
        verbose_name = "employee"
        verbose_name_plural = "employees"


class Driver(Common):
    """
    Person who delivers orders to clients
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver",
    )

    class Meta:
        verbose_name = "driver"
        verbose_name_plural = "drivers"


class Client(Common):
    """
    Online-only clients of application. They used our application to
    make orders and request pickups.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    package = models.ForeignKey(
        "core.Package",
        null=True,
        on_delete=models.CASCADE,
        related_name="profile_list",
    )
    phone = models.CharField(
        max_length=15,
        default="",
    )

    # Additional employee information
    DOB = models.DateField(
        null=True,
    )
    joining_date = models.DateField(
        null=True,
    )
    SSN = models.CharField(
        max_length=15,
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
