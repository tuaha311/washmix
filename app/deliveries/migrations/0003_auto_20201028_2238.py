# Generated by Django 2.2.16 on 2020-10-29 05:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("locations", "0001_initial"),
        ("deliveries", "0002_schedule_address"),
        ("billing", "0002_auto_20201028_2238"),
    ]

    operations = [
        migrations.AddField(
            model_name="schedule",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="schedule_list",
                to="users.Client",
                verbose_name="client",
            ),
        ),
        migrations.AddField(
            model_name="request",
            name="address",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="request_list",
                to="locations.Address",
                verbose_name="address to pickup and dropoff",
            ),
        ),
        migrations.AddField(
            model_name="request",
            name="client",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="request_list",
                to="users.Client",
                verbose_name="client",
            ),
        ),
        migrations.AddField(
            model_name="request",
            name="schedule",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="request_list",
                to="deliveries.Schedule",
                verbose_name="recurring schedule for request",
            ),
        ),
        migrations.AddField(
            model_name="delivery",
            name="employee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="delivery_list",
                to="users.Employee",
                verbose_name="employee that handles this delivery",
            ),
        ),
        migrations.AddField(
            model_name="delivery",
            name="invoice",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="delivery",
                to="billing.Invoice",
                verbose_name="invoice for delivery",
            ),
        ),
        migrations.AddField(
            model_name="delivery",
            name="request",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="delivery_list",
                to="deliveries.Request",
                verbose_name="request",
            ),
        ),
        migrations.AlterUniqueTogether(name="delivery", unique_together={("request", "kind")},),
    ]
