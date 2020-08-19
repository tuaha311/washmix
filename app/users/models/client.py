from django.conf import settings
from django.db import models

from core.common_models import Common
from modules.enums import Crease, Detergents, Starch
from users.managers import ClientManager


class Client(Common):
    """
    ONLINE-ONLY clients of application. They use our web-application to
    make orders and request pickups. Our main targeted audience.

    To this client we can offer a full-featured web-application without any
    restrictions. This kind of client can login into application, because they
    have an relation with authentication data (AUTH_USER_MODEL).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client",
    )
    package = models.ForeignKey(
        "billing.Package",
        verbose_name="package of service",
        related_name="client_list",
        on_delete=models.CASCADE,
        null=True,
    )
    main_card = models.OneToOneField(
        "billing.Card",
        verbose_name="main card",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
    )
    main_phone = models.OneToOneField(
        "core.Phone",
        verbose_name="main phone number",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
    )
    main_address = models.OneToOneField(
        "locations.Address",
        verbose_name="main address",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
    )

    # Customer information
    has_doormen = models.BooleanField(
        default=False,
    )
    stripe_customer_id = models.TextField(
        null=True,
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
    fabric_softener = models.BooleanField(
        default=False,
    )
    fix_tears = models.BooleanField(
        default=False,
    )

    objects = ClientManager()

    class Meta:
        verbose_name = "client"
        verbose_name_plural = "clients"

    @property
    def email(self):
        return self.user.email

    @property
    def first_name(self):
        return self.user.first_name

    @first_name.setter
    def first_name(self, value: str):
        self.user.first_name = value
        self.user.save()

    @property
    def last_name(self):
        return self.user.last_name

    @last_name.setter
    def last_name(self, value: str):
        self.user.last_name = value
        self.user.save()

    def __str__(self):
        return self.email
