# Generated by Django 2.2.15 on 2020-08-18 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_add_validator_for_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='zip_code',
            field=models.CharField(blank=True, max_length=20, verbose_name='zip code'),
        ),
    ]
