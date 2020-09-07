from django.conf import settings
from django.db import models
from django.db.models import Sum

from billing.models.transaction import Transaction
from core.behaviors import Stripeable
from core.common_models import Common
from modules.enums import Crease, Detergents, Starch
from users.managers import ClientManager


class Client(Stripeable, Common):
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
    subscription = models.ForeignKey(
        "billing.Subscription",
        verbose_name="subscription of service",
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
    is_auto_billing = models.BooleanField(
        verbose_name="automatically bill subscription",
        default=True,
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

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def balance(self):
        debit_transactions = self.transaction_list.filter(kind=Transaction.DEBIT)
        credit_transactions = self.transaction_list.filter(kind=Transaction.CREDIT)

        debit_total = debit_transactions.aggregate(total=Sum('amount'))['total'] or 0
        credit_total = credit_transactions.aggregate(total=Sum('amount'))['total'] or 0

        return debit_total - credit_total

    def __str__(self):
        return self.email
