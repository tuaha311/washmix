# Generated by Django 2.2.15 on 2020-08-21 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0003_add_stripe_id_on_card_and_transaction"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coupon",
            name="code",
            field=models.CharField(max_length=30, unique=True, verbose_name="code"),
        ),
    ]
