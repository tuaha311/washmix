# Generated by Django 2.2.24 on 2022-03-01 23:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_change_defaults_for_client"),
        ("notifications", "0005_auto_20220301_1414"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="customer_triggered",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users.Customer",
                verbose_name="customer",
            ),
        ),
    ]
