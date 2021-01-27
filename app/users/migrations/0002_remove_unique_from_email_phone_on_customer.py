# Generated by Django 2.2.17 on 2021-01-26 07:18

from django.db import migrations, models

import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name="email"),
        ),
        migrations.AlterField(
            model_name="customer",
            name="phone",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                validators=[core.validators.validate_phone],
                verbose_name="phone",
            ),
        ),
    ]
