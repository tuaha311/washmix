# Generated by Django 2.2.17 on 2021-02-09 06:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("locations", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="address_list",
                to="users.Client",
                verbose_name="client",
            ),
        ),
        migrations.AddField(
            model_name="address",
            name="zip_code",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="address_list",
                to="locations.ZipCode",
                verbose_name="zip code",
            ),
        ),
    ]
