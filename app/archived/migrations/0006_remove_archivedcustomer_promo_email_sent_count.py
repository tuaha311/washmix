# Generated by Django 2.2.28 on 2023-11-10 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archived', '0005_archivedcustomer_promo_email_sent_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='archivedcustomer',
            name='promo_email_sent_count',
        ),
    ]
