# Generated by Django 2.2.16 on 2020-10-06 09:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
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
            ],
            options={"verbose_name": "package", "verbose_name_plural": "packages",},
        ),
        migrations.CreateModel(
            name="Subscription",
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
                (
                    "name",
                    models.CharField(
                        choices=[("payc", "PAYC"), ("gold", "GOLD"), ("platinum", "PLATINUM")],
                        max_length=20,
                        verbose_name="name",
                    ),
                ),
                (
                    "invoice",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscription",
                        to="billing.Invoice",
                        verbose_name="invoice",
                    ),
                ),
            ],
            options={"verbose_name": "subscription", "verbose_name_plural": "subscriptions",},
        ),
    ]
