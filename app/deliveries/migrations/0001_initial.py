# Generated by Django 2.2.16 on 2020-10-29 05:38

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Delivery",
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
                    "kind",
                    models.CharField(
                        choices=[("pickup", "Pickup"), ("dropoff", "Dropoff")],
                        default="pickup",
                        max_length=10,
                        verbose_name="kind of delivery",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("accepted", "Accepted"),
                            ("in_progress", "In progress"),
                            ("completed", "Completed"),
                        ],
                        default="accepted",
                        max_length=20,
                        verbose_name="current status",
                    ),
                ),
                ("date", models.DateField(verbose_name="date for delivery")),
                ("start", models.TimeField(verbose_name="start of delivery interval")),
                ("end", models.TimeField(verbose_name="end of delivery interval")),
            ],
            options={
                "verbose_name": "delivery",
                "verbose_name_plural": "deliveries",
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="Request",
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
                ("comment", models.TextField(blank=True, verbose_name="comment")),
                (
                    "is_rush",
                    models.BooleanField(default=False, verbose_name="is a rush / urgent delivery"),
                ),
            ],
            options={"verbose_name": "request", "verbose_name_plural": "requests",},
        ),
        migrations.CreateModel(
            name="Schedule",
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
                ("comment", models.TextField(blank=True, verbose_name="comment")),
                (
                    "is_rush",
                    models.BooleanField(default=False, verbose_name="is a rush / urgent delivery"),
                ),
                (
                    "days",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.PositiveSmallIntegerField(
                            choices=[
                                (1, "Monday"),
                                (2, "Tuesday"),
                                (3, "Wednesday"),
                                (4, "Thursday"),
                                (5, "Friday"),
                                (6, "Saturday"),
                                (7, "Sunday"),
                            ],
                            verbose_name="day of week",
                        ),
                        max_length=7,
                        size=None,
                        verbose_name="recurring pickup days",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active recurring delivery"),
                            ("paused", "Paused recurring delivery"),
                        ],
                        max_length=20,
                        verbose_name="status of schedule",
                    ),
                ),
            ],
            options={"verbose_name": "schedule", "verbose_name_plural": "schedules",},
        ),
    ]
