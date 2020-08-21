# Generated by Django 2.2.15 on 2020-08-21 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_add_foreign_keys'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='stripe_card_id',
        ),
        migrations.AddField(
            model_name='card',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Stripe ID'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Stripe ID'),
        ),
    ]
