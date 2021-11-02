# Generated by Django 2.2.24 on 2021-10-25 13:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0002_change_defaults_for_client"),
        ("notifications", "0003_delete_notification"),
    ]

    operations = [
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
                (
                    "message",
                    models.CharField(
                        choices=[
                            ("new_order", "created new order"),
                            ("new_signup", "signed up"),
                            ("new_pickup_request", "created new pickup request"),
                            ("pickup_date_change", "changed the pickup date"),
                            ("pickup_request_canceled", "canceled the pickup request"),
                            ("dropoff_due_today", "drop-off is due today"),
                        ],
                        max_length=80,
                        verbose_name="notification type",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        choices=[
                            ("new_order", "created new order"),
                            ("new_signup", "signed up"),
                            ("new_pickup_request", "created new pickup request"),
                            ("pickup_date_change", "changed the pickup date"),
                            ("pickup_request_canceled", "canceled the pickup request"),
                            ("dropoff_due_today", "drop-off is due today"),
                        ],
                        max_length=100,
                        null=True,
                        verbose_name="short description",
                    ),
                ),
                ("is_read", models.BooleanField(default=False, verbose_name="message read")),
                (
                    "user_triggered",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.Client",
                        verbose_name="client",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
            },
        ),
    ]
