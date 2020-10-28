# Generated by Django 2.2.16 on 2020-10-28 05:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0002_set_foreign_keys"),
        ("billing", "0004_remove_coupon_from_invoice"),
        ("orders", "0003_add_unique_together_on_order"),
    ]

    operations = [
        migrations.RemoveField(model_name="order", name="invoice_list",),
        migrations.AddField(
            model_name="order",
            name="coupon",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="invoice_list",
                to="billing.Coupon",
                verbose_name="coupon",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="subscription",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order",
                to="subscriptions.Subscription",
                verbose_name="subscription",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="basket",
            field=models.OneToOneField(
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
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order",
                to="deliveries.Request",
                verbose_name="request",
            ),
        ),
    ]
