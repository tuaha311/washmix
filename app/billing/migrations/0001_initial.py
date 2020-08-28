# Generated by Django 2.2.15 on 2020-08-28 13:13

import django.utils.timezone
from django.db import migrations, models

import modules.enums


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
            options={"verbose_name": "card", "verbose_name_plural": "cards",},
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
                            (modules.enums.CouponType("FIRST"), "FIRST"),
                            (modules.enums.CouponType("PACKAGE"), "PACKAGE"),
                        ],
                        default="FIRST",
                        max_length=30,
                        null=True,
                        verbose_name="coupon type",
                    ),
                ),
            ],
            options={"verbose_name": "coupon", "verbose_name_plural": "coupons",},
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
                (
                    "_object_id",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="ID of related object"
                    ),
                ),
            ],
            options={"verbose_name": "invoice", "verbose_name_plural": "invoices",},
        ),
        migrations.CreateModel(
            name="Package",
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
                ("price", models.BigIntegerField(verbose_name="price in cents (¢)")),
                (
                    "name",
                    models.CharField(
                        choices=[("payc", "PAYC"), ("gold", "GOLD"), ("platinum", "PLATINUM")],
                        max_length=20,
                        unique=True,
                        verbose_name="name",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="description of package"
                    ),
                ),
                ("dry_clean", models.IntegerField(verbose_name="discount on dry clean + press")),
                ("laundry", models.IntegerField(verbose_name="discount on laundry + press")),
                ("alterations", models.IntegerField(verbose_name="alterations discount")),
                ("wash_fold", models.IntegerField(verbose_name="discount on wash & fold")),
                ("has_delivery", models.BooleanField(verbose_name="has a free delivery")),
                ("has_welcome_box", models.BooleanField(verbose_name="has a welcome box")),
                (
                    "has_seasonal_garment",
                    models.BooleanField(verbose_name="has a seasonal garment storage"),
                ),
                ("has_credit_back", models.BooleanField(verbose_name="has a credit back")),
                (
                    "is_most_popular",
                    models.BooleanField(default=False, verbose_name="most popular badge"),
                ),
            ],
            options={"verbose_name": "package", "verbose_name_plural": "packages",},
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
                        ],
                        max_length=10,
                        verbose_name="provider of transaction",
                    ),
                ),
            ],
            options={"verbose_name": "transaction", "verbose_name_plural": "transactions",},
        ),
    ]
