# Generated by Django 2.2.17 on 2021-02-09 09:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0003_set_default_values"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="subscription",
            name="invoice",
        ),
    ]
