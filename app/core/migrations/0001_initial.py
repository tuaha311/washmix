# Generated by Django 2.1.1 on 2020-07-10 08:58
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import modules.enums


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
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
                ("address_line_1", models.TextField()),
                ("address_line_2", models.TextField(default="")),
                ("state", models.CharField(default="", max_length=30)),
                ("city", models.CharField(max_length=30)),
                ("zip_code", models.CharField(max_length=30)),
                ("title", models.CharField(default="", max_length=80)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="address_list",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False,},
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
                ("name", models.CharField(max_length=30)),
                ("amount_off", models.FloatField(default=0)),
                ("percentage_off", models.FloatField(default=0)),
                ("start_date", models.DateTimeField(default=django.utils.timezone.localtime)),
                ("valid", models.BooleanField(default=True)),
                ("max_redemptions", models.IntegerField(default=1)),
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
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Notification",
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
                ("message", models.TextField(default="")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={"abstract": False,},
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
                ("name", models.TextField(default="")),
                ("price", models.FloatField(default=0)),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Product",
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
                ("name", models.CharField(max_length=50)),
                ("price", models.FloatField(default=0)),
                (
                    "product",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="core.Product",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
    ]
