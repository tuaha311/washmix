# Generated by Django 2.2.14 on 2020-07-31 11:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
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
                ("message", models.TextField(verbose_name="message")),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_list",
                        to="users.Client",
                        verbose_name="client",
                    ),
                ),
            ],
            options={"verbose_name": "notification", "verbose_name_plural": "notifications",},
        ),
    ]
