# Generated by Django 2.2.14 on 2020-08-03 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_add_phone_client"),
    ]

    operations = [
        migrations.AlterField(
            model_name="phone",
            name="number",
            field=models.CharField(max_length=20, unique=True, verbose_name="number"),
        ),
    ]
