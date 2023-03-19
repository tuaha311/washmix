# Generated by Django 2.2.17 on 2021-02-09 06:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("subscriptions", "0001_initial"),
        ("users", "0001_initial"),
        ("orders", "0001_initial"),
        ("billing", "0002_set_foreign_keys"),
        ("deliveries", "0003_set_foreign_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_list",
                to="users.Client",
                verbose_name="client",
            ),
        ),
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
            name="employee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="order_list",
                to="users.Employee",
                verbose_name="employee who handles this order",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="invoice",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order",
                to="billing.Invoice",
                verbose_name="invoice for basket",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="request",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="order",
                to="deliveries.Request",
                verbose_name="request",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="subscription",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="order",
                to="subscriptions.Subscription",
                verbose_name="subscription",
            ),
        ),
        migrations.AddField(
            model_name="basket",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="basket_list",
                to="users.Client",
                verbose_name="client",
            ),
        ),
        migrations.AddField(
            model_name="basket",
            name="item_list",
            field=models.ManyToManyField(
                related_name="basket_list",
                through="orders.Quantity",
                to="orders.Price",
                verbose_name="items in basket",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="price",
            unique_together={("service", "item")},
        ),
        migrations.AlterUniqueTogether(
            name="order",
            unique_together={("basket", "request")},
        ),
    ]
