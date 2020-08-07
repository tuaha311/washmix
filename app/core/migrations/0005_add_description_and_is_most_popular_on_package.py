# Generated by Django 2.2.15 on 2020-08-07 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_validator_for_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='description',
            field=models.CharField(blank=True, max_length=100, verbose_name='description of package'),
        ),
        migrations.AddField(
            model_name='package',
            name='is_most_popular',
            field=models.BooleanField(default=False, verbose_name='most popular badge'),
        ),
    ]
