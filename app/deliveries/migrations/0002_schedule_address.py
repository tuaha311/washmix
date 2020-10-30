# Generated by Django 2.2.16 on 2020-10-30 03:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("locations", "0001_initial"),
        ("deliveries", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="schedule",
            name="address",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="schedule_list",
                to="locations.Address",
                verbose_name="address to pickup and dropoff",
            ),
        ),
    ]
