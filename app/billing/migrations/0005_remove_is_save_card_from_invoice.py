# Generated by Django 2.2.16 on 2020-10-29 04:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0004_remove_coupon_from_invoice"),
    ]

    operations = [
        migrations.RemoveField(model_name="invoice", name="is_save_card",),
    ]
