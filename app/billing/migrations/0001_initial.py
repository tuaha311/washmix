# Generated by Django 2.2.16 on 2020-10-30 03:08

import django.contrib.postgres.fields.jsonb
import django.utils.timezone
from django.db import migrations, models

import core.mixins
import legacy.enums


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Card",
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
                ("last", models.CharField(max_length=4, verbose_name="last 4 digits")),
                (
                    "expiration_month",
                    models.PositiveSmallIntegerField(verbose_name="expiration month"),
                ),
                (
                    "expiration_year",
                    models.PositiveSmallIntegerField(verbose_name="expiration year"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="card is active")),
            ],
            options={
                "verbose_name": "card",
                "verbose_name_plural": "cards",
            },
        ),
        migrations.CreateModel(
            name="Coupon",
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
                ("code", models.CharField(max_length=30, unique=True, verbose_name="code")),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="description or note for coupon"
                    ),
                ),
                (
                    "discount_by",
                    models.CharField(
                        choices=[
                            ("percentage", "Discount by percentage"),
                            ("amount", "Discount by amount"),
                        ],
                        default="amount",
                        max_length=10,
                    ),
                ),
                (
                    "value_off",
                    models.BigIntegerField(
                        default=0,
                        help_text="for discount by percentage - it will be percentage in % of discount;\nfor discount by amount - it will be amount in cents (¢) of discount",
                        verbose_name="value of discount",
                    ),
                ),
                (
                    "end_date",
                    models.DateTimeField(
                        default=django.utils.timezone.localtime, verbose_name="end date of coupon"
                    ),
                ),
                (
                    "is_valid",
                    models.BooleanField(default=True, verbose_name="is coupon valid for apply"),
                ),
                (
                    "max_redemptions",
                    models.IntegerField(default=1, verbose_name="maximum count of redemptions"),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            (legacy.enums.CouponType("FIRST"), "FIRST"),
                            (legacy.enums.CouponType("PACKAGE"), "PACKAGE"),
                        ],
                        default="FIRST",
                        max_length=30,
                        null=True,
                        verbose_name="coupon type",
                    ),
                ),
            ],
            options={
                "verbose_name": "coupon",
                "verbose_name_plural": "coupons",
            },
        ),
        migrations.CreateModel(
            name="Invoice",
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
                ("amount", models.BigIntegerField(verbose_name="amount in cents (¢)")),
                ("discount", models.BigIntegerField(verbose_name="discount in cents (¢)")),
                (
                    "purpose",
                    models.CharField(
                        choices=[
                            ("subscription", "Subscription purchase"),
                            ("basket", "Order processing payment"),
                            ("delivery", "Payment for delivery"),
                        ],
                        default="subscription",
                        max_length=20,
                        verbose_name="purpose of this invoice",
                    ),
                ),
            ],
            options={
                "verbose_name": "invoice",
                "verbose_name_plural": "invoices",
            },
            bases=(core.mixins.CalculatedAmountWithDiscount, models.Model),
        ),
        migrations.CreateModel(
            name="Transaction",
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
                ("amount", models.BigIntegerField(verbose_name="amount in cents (¢)")),
                (
                    "kind",
                    models.CharField(
                        choices=[("debit", "Debit"), ("credit", "Credit")],
                        max_length=10,
                        verbose_name="kind of transaction",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        choices=[
                            ("stripe", "Stripe"),
                            ("coupon", "Coupon"),
                            ("credit_back", "Credit back"),
                            ("washmix", "WashMix"),
                        ],
                        max_length=10,
                        verbose_name="provider of transaction",
                    ),
                ),
                (
                    "source",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=dict, verbose_name="source of transaction (Stripe raw data)"
                    ),
                ),
            ],
            options={
                "verbose_name": "transaction",
                "verbose_name_plural": "transactions",
            },
        ),
    ]
