# Generated by Django 2.2.16 on 2020-11-18 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0002_auto_20201029_2008"),
    ]

    operations = [
        migrations.AlterField(
            model_name="package",
            name="name",
            field=models.CharField(
                choices=[
                    ("payc", "Pay As You Clean"),
                    ("gold", "Gold Account"),
                    ("platinum", "Platinum Account"),
                ],
                max_length=20,
                unique=True,
                verbose_name="name",
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="name",
            field=models.CharField(
                choices=[
                    ("payc", "Pay As You Clean"),
                    ("gold", "Gold Account"),
                    ("platinum", "Platinum Account"),
                ],
                max_length=20,
                verbose_name="name",
            ),
        ),
    ]
