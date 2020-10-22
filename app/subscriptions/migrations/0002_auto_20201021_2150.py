# Generated by Django 2.2.16 on 2020-10-22 04:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("subscriptions", "0001_initial"),
        ("billing", "0002_auto_20201021_2150"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subscription_list",
                to="users.Client",
                verbose_name="client",
            ),
        ),
        migrations.AddField(
            model_name="subscription",
            name="invoice",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subscription",
                to="billing.Invoice",
                verbose_name="invoice",
            ),
        ),
    ]
