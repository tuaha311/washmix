# Generated by Django 2.2.17 on 2021-02-24 04:02

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("deliveries", "0006_add_is_custom_on_request"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schedule",
            name="days",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(
                    choices=[
                        (1, "Monday"),
                        (2, "Tuesday"),
                        (3, "Wednesday"),
                        (4, "Thursday"),
                        (5, "Friday"),
                        (6, "Saturday"),
                    ],
                    verbose_name="day of week",
                ),
                max_length=5,
                size=None,
                verbose_name="recurring pickup days",
            ),
        ),
    ]
