from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum

from billing.choices import InvoiceKind
from core.behaviors import Stripeable
from core.common_models import Common
from core.utils import get_dollars
from users.choices import ClientCrease, ClientDetergents, ClientStarch
from users.managers import ClientManager
from users.mixins import ProxyUserInfoMixin
from django.utils.timezone import localtime, timedelta


class Client(ProxyUserInfoMixin, Stripeable, Common):
    """
    Client-side entity.

    ONLINE-ONLY clients of application. They use our web-application to
    make orders and request deliveries. Our main targeted audience.

    To this client we can offer a full-featured web-application without any
    restrictions. This kind of client can login into application, because they
    have an relation with authentication data (AUTH_USER_MODEL).

    IMPORTANT: Client entity has a signal receiver on `post_save`.
    Signal location - `users.signals`
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
    starch = models.CharField(
        max_length=20,
        verbose_name="starch",
        choices=ClientStarch.CHOICES,
        default=ClientStarch.NONE,
        blank=True,
    )
    no_crease = models.CharField(
        max_length=20,
        verbose_name="no crease",
        choices=ClientCrease.CHOICES,
        default=ClientCrease.ALL_PANTS,
        blank=True,
    )
    fix_tears = models.BooleanField(
        verbose_name="fix tears, rips",
        default=True,
    )
    detergents = models.CharField(
        max_length=20,
        choices=ClientDetergents.CHOICES,
        blank=True,
    )
    fabric_softener = models.BooleanField(
        verbose_name="fabric softener",
        default=False,
    )
    # this flag used for automatic subscription purchase
    # when balance is lower than AUTO_BILLING_LIMIT
    is_auto_billing = models.BooleanField(
        verbose_name="automatically bill subscription",
        default=True,
    )

    private_note = models.CharField(
        max_length=300,
        blank=True,
    )
    
    promo_sms_notification = models.DateField(
        verbose_name="Promotional SMS Date",
        editable=False,
        blank=True,
        null=True,
    )

    objects = ClientManager()

    class Meta:
        verbose_name = "client"
        verbose_name_plural = "clients"

    def _balance(self):
        debit_transactions = self.transaction_list.filter(kind=InvoiceKind.DEBIT)
        credit_transactions = self.transaction_list.filter(kind=InvoiceKind.CREDIT)

        debit_total = debit_transactions.aggregate(total=Sum("amount"))["total"] or 0
        credit_total = credit_transactions.aggregate(total=Sum("amount"))["total"] or 0

        return debit_total - credit_total
    _balance.short_description = 'Balance, in cents (¢)'  # type: ignore
    balance = property(_balance)
    
    @property
    def dollar_balance(self):
        return get_dollars(self, "balance")

    @property
    def pretty_billing_address(self):
        values = self.billing_address.values()

        return ", ".join(values)

    @property
    def full_name(self):
        full_name = f"{self.first_name} {self.last_name}"

        if full_name == " ":
            full_name = "Customer"

        return full_name

    @property
    def has_card(self):
        card_list = self.card_list.all()
        has_card = card_list.exists()

        return has_card

    def __str__(self):
        return self.email

    def set_promo_sms_sent_date(self, value):
        print("SETTING PROMO SMS SENT DATE")
        self.promo_sms_notification = value

    def save(self, *args, **kwargs):
        if not self.promo_sms_notification:
            self.promo_sms_notification = (localtime() + timedelta(days=60)).date()
        super().save(*args, **kwargs)