# Generated by Django 2.2.15 on 2020-08-19 14:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transaction_list",
                to="users.Client",
                verbose_name="client",
            ),
        ),
        migrations.AddField(
            model_name="card",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="card_list",
                to="users.Client",
                verbose_name="client",
            ),
        ),
    ]
