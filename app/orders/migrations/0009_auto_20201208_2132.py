# Generated by Django 2.2.17 on 2020-12-09 05:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0008_auto_20201201_1814"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="basket",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order",
                to="orders.Basket",
                verbose_name="basket",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="request",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order",
                to="deliveries.Request",
                verbose_name="request",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="subscription",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order",
                to="subscriptions.Subscription",
                verbose_name="subscription",
            ),
        ),
    ]
