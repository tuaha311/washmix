# Generated by Django 2.2.28 on 2023-10-13 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_set_foreign_keys'),
        ('deliveries', '0016_auto_20231013_0707'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='in_store',
            field=models.BooleanField(blank=True, default=False, editable=False, null=True, verbose_name='Instore delivery'),
        ),
        migrations.CreateModel(
            name='CategorizeRoute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('changed', models.DateTimeField(auto_now=True, verbose_name='last changed date and time')),
                ('day', models.CharField(choices=[('1', 'Monday'), ('2', 'Tuesday'), ('3', 'Wednesday'), ('4', 'Thursday'), ('5', 'Friday'), ('6', 'Saturday'), ('7', 'Sunday')], max_length=2, unique=True, verbose_name='Day')),
                ('zip_codes', models.ManyToManyField(to='locations.ZipCode', verbose_name='Zip Codes')),
            ],
            options={
                'verbose_name_plural': 'Categorized Routes',
            },
        ),
    ]
