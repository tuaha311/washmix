# Generated by Django 2.2.17 on 2021-01-19 04:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_set_foreign_keys"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="is_pdf_ready",
        ),
    ]
