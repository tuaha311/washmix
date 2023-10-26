import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import core.validators
import users.mixins


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("subscriptions", "0001_initial"),
        ("billing", "0001_initial"),
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="creation date and time"),
                ),
                (
                    "changed",
                    models.DateTimeField(auto_now=True, verbose_name="last changed date and time"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, null=True, verbose_name="email"),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        null=True,
                        validators=[core.validators.validate_phone],
                        verbose_name="phone",
                    ),
                ),
                (
                    "full_name",
                    models.CharField(blank=True, max_length=100, verbose_name="full name"),
                ),
                ("zip_code", models.CharField(blank=True, max_length=20, verbose_name="zip code")),
                ("address", models.CharField(blank=True, max_length=250, verbose_name="address")),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("interested", "Who interested in our services in future"),
                            (
                                "possible",
                                "Who uses only SMS orders and maybe will use web-application in future",
                            ),
                            ("storage", "Who interested in garment storage in our warehouse"),
                        ],
                        default="interested",
                        max_length=20,
                        verbose_name="kind",
                    ),
                ),
            ],
            options={
                "verbose_name": "Potential Customer",
                "verbose_name_plural": "Potential Customers",
            },
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="creation date and time"),
                ),
                (
                    "changed",
                    models.DateTimeField(auto_now=True, verbose_name="last changed date and time"),
                ),
                (
                    "position",
                    models.CharField(
                        choices=[
                            ("driver", "Driver"),
                            ("laundress", "Laundress"),
                            ("manager", "Manager"),
                        ],
                        default="laundress",
                        max_length=20,
                        verbose_name="position of employee",
                    ),
                ),
                (
                    "SSN",
                    models.CharField(
                        max_length=15, null=True, verbose_name="social security number"
                    ),
                ),
                (
                    "birthday",
                    models.DateField(
                        default=django.utils.timezone.localdate,
                        null=True,
                        verbose_name="date of birthday",
                    ),
                ),
                (
                    "came_to_work",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        null=True,
                        verbose_name="came out to work from",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employee",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "employee",
                "verbose_name_plural": "employees",
            },
            bases=(users.mixins.ProxyUserInfoMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="creation date and time"),
                ),
                (
                    "changed",
                    models.DateTimeField(auto_now=True, verbose_name="last changed date and time"),
                ),
                (
                    "stripe_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, unique=True, verbose_name="Stripe ID"
                    ),
                ),
                (
                    "billing_address",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="billing address"
                    ),
                ),
                (
                    "detergents",
                    models.CharField(
                        blank=True,
                        choices=[("scented", "Scented"), ("hypo_allergenic", "Hypo-Allergenic")],
                        max_length=20,
                    ),
                ),
                (
                    "starch",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("none", "None"),
                            ("light", "Light"),
                            ("medium", "Medium"),
                            ("heavy", "Heavy"),
                        ],
                        max_length=20,
                        verbose_name="starch",
                    ),
                ),
                (
                    "no_crease",
                    models.CharField(
                        blank=True,
                        choices=[("all_pants", "All Pants"), ("jeans_only", "Jeans Only")],
                        max_length=20,
                        verbose_name="no crease",
                    ),
                ),
                (
                    "fabric_softener",
                    models.BooleanField(default=False, verbose_name="fabric softener"),
                ),
                ("fix_tears", models.BooleanField(default=False, verbose_name="fix tears, rips")),
                (
                    "is_auto_billing",
                    models.BooleanField(
                        default=True, verbose_name="automatically bill subscription"
                    ),
                ),
                (
                    "main_address",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="locations.Address",
                        verbose_name="main address",
                    ),
                ),
                (
                    "main_card",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="billing.Card",
                        verbose_name="main card",
                    ),
                ),
                (
                    "main_phone",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="core.Phone",
                        verbose_name="main phone number",
                    ),
                ),
                (
                    "subscription",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="active_client",
                        to="subscriptions.Subscription",
                        verbose_name="subscription of service",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="client",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "client",
                "verbose_name_plural": "clients",
            },
            bases=(users.mixins.ProxyUserInfoMixin, models.Model),
        ),
    ]
