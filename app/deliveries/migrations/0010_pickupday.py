# Generated by Django 2.2.24 on 2022-06-13 13:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("deliveries", "0009_auto_20220301_1414"),
    ]

    operations = [
        migrations.CreateModel(
            name="PickupDay",
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
                    "day",
                    models.CharField(
                        blank=True,
                        choices=[
                            (1, "Monday"),
                            (2, "Tuesday"),
                            (3, "Wednesday"),
                            (4, "Thursday"),
                            (5, "Friday"),
                            (6, "Saturday"),
                            (7, "Sunday"),
                        ],
                        max_length=20,
                        null=True,
                        verbose_name="current status",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
