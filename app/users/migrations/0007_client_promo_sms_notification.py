# Generated by Django 2.2.28 on 2023-09-20 18:40

import datetime
from django.db import migrations, models
from django.utils.timezone import localtime, timedelta

def calculate_default_promo_sms_date(apps, schema_editor):
    return (localtime() + timedelta(days=60)).date()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20230407_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='promo_sms_notification',
            field=models.DateField(
                blank=True,
                default=calculate_default_promo_sms_date,
                editable=False,
                null=True,
                verbose_name='Promotional SMS Date'
            ),
        ),
    ]
