# Generated by Django 2.2.15 on 2020-08-24 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_add_stripe_id_on_client"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="stripe_id",
            field=models.CharField(
                blank=True, max_length=100, unique=True, null=True, verbose_name="Stripe ID"
            ),
        ),
    ]
