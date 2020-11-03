# Generated by Django 2.2.16 on 2020-11-03 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_auto_20201101_2356"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="kind",
            field=models.CharField(
                choices=[
                    ("interested", "Who interested in our services in future"),
                    (
                        "possible",
                        "Who uses only SMS orders and maybe will use web-application in future",
                    ),
                    ("storage", "Who interested in garment storage in our warehouse"),
                ],
                max_length=20,
                verbose_name="kind",
            ),
        ),
    ]
