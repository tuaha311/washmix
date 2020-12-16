from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum

from billing.choices import Kind
from core.behaviors import Stripeable
from core.common_models import Common
from core.utils import get_dollars
from users.choices import Crease, Detergents, Starch
from users.managers import ClientManager
from users.mixins import ProxyUserInfoMixin


class Client(ProxyUserInfoMixin, Stripeable, Common):
    """
    Client-side entity.

    ONLINE-ONLY clients of application. They use our web-application to
    make orders and request deliveries. Our main targeted audience.

    To this client we can offer a full-featured web-application without any
    restrictions. This kind of client can login into application, because they
    have an relation with authentication data (AUTH_USER_MODEL).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client",
    )
    subscription = models.OneToOneField(
        "subscriptions.Subscription",
        verbose_name="subscription of service",
        related_name="active_client",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    main_card = models.OneToOneField(
        "billing.Card",
        verbose_name="main card",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    main_phone = models.OneToOneField(
        "core.Phone",
        verbose_name="main phone number",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    main_address = models.OneToOneField(
        "locations.Address",
        verbose_name="main address",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    billing_address = JSONField(
        verbose_name="billing address",
        default=dict,
        blank=True,
    )

    # Preferences
    detergents = models.CharField(
        max_length=20,
        choices=Detergents.CHOICES,
        blank=True,
    )
    starch = models.CharField(
        max_length=20,
        verbose_name="starch",
        choices=Starch.CHOICES,
        blank=True,
    )
    no_crease = models.CharField(
        max_length=20,
        verbose_name="no crease",
        choices=Crease.CHOICES,
        blank=True,
    )
    fabric_softener = models.BooleanField(
        verbose_name="fabric softener",
        default=False,
    )
    fix_tears = models.BooleanField(
        verbose_name="fix tears, rips",
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

    def _balance(self):
        debit_transactions = self.transaction_list.filter(kind=Kind.DEBIT)
        credit_transactions = self.transaction_list.filter(kind=Kind.CREDIT)

        debit_total = debit_transactions.aggregate(total=Sum("amount"))["total"] or 0
        credit_total = credit_transactions.aggregate(total=Sum("amount"))["total"] or 0

        return debit_total - credit_total
    _balance.short_description = 'Balance, in cents (¢)'
    balance = property(_balance)
    
    @property
    def dollar_balance(self):
        return get_dollars(self, "balance")

    @property
    def pretty_billing_address(self):
        values = self.billing_address.values()

        return ", ".join(values)

    def __str__(self):
        return self.email
