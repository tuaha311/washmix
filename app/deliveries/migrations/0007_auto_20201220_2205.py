# Generated by Django 2.2.17 on 2020-12-21 06:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("deliveries", "0006_auto_20201220_2205"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="delivery",
            options={
                "ordering": ["employee", "-date", "sorting"],
                "verbose_name": "delivery",
                "verbose_name_plural": "deliveries",
            },
        ),
    ]
