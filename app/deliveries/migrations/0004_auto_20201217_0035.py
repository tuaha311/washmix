# Generated by Django 2.2.17 on 2020-12-17 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("deliveries", "0003_auto_20201210_2357"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="delivery",
            options={
                "ordering": ["-date", "sorting"],
                "verbose_name": "delivery",
                "verbose_name_plural": "deliveries",
            },
        ),
        migrations.RemoveField(
            model_name="delivery",
            name="priority",
        ),
        migrations.AddField(
            model_name="delivery",
            name="sorting",
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="sorting"),
        ),
    ]
