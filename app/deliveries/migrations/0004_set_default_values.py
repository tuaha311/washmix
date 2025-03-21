# Generated by Django 2.2.17 on 2021-02-09 07:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("deliveries", "0003_set_foreign_keys"),
    ]

    operations = [
        migrations.AlterField(
            model_name="request",
            name="amount",
            field=models.BigIntegerField(default=0, verbose_name="amount, in cents (¢)"),
        ),
        migrations.AlterField(
            model_name="request",
            name="discount",
            field=models.FloatField(default=0, verbose_name="discount, in cents (¢)"),
        ),
    ]
