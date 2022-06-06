# Generated by Django 2.2.24 on 2022-05-24 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_change_defaults_for_client"),
    ]

    operations = [
        migrations.CreateModel(
            name="Logs",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="creation date and time"),
                ),
                (
                    "changed",
                    models.DateTimeField(auto_now=True, verbose_name="last changed date and time"),
                ),
                ("action", models.CharField(max_length=255)),
                ("customer", models.CharField(max_length=255)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
