# Generated by Django 2.2.14 on 2020-07-24 08:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import modules.enums


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('changed', models.DateTimeField(auto_now=True, verbose_name='last changed date and time')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('changed', models.DateTimeField(auto_now=True, verbose_name='last changed date and time')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('changed', models.DateTimeField(auto_now=True, verbose_name='last changed date and time')),
                ('phone', models.CharField(default='', max_length=15)),
                ('DOB', models.DateField(null=True)),
                ('joining_date', models.DateField(null=True)),
                ('SSN', models.CharField(max_length=15, null=True)),
                ('is_doormen', models.BooleanField(default=False)),
                ('stripe_customer_id', models.TextField(null=True)),
                ('balance', models.FloatField(default=0)),
                ('detergents', models.CharField(choices=[(modules.enums.Detergents('Scented'), 'Scented'), (modules.enums.Detergents('Hypo-Allergenic'), 'Hypo-Allergenic')], max_length=50, null=True)),
                ('starch', models.CharField(choices=[(modules.enums.Starch('NONE'), 'NONE'), (modules.enums.Starch('LIGHT'), 'LIGHT'), (modules.enums.Starch('MEDIUM'), 'MEDIUM'), (modules.enums.Starch('HEAVY'), 'HEAVY')], max_length=50, null=True)),
                ('no_crease', models.CharField(choices=[(modules.enums.Crease('ALL_PANTS'), 'ALL_PANTS'), (modules.enums.Crease('JEANS_ONLY'), 'JEANS_ONLY')], max_length=50, null=True)),
                ('app_users', models.CharField(choices=[(modules.enums.AppUsers('POTENTIAL_USERS'), 'POTENTIAL_USERS'), (modules.enums.AppUsers('REGULAR_USERS'), 'REGULAR_USERS'), (modules.enums.AppUsers('EMPLOYEE'), 'EMPLOYEE')], default='REGULAR_USERS', max_length=30, null=True)),
                ('authentication_provider', models.CharField(choices=[(modules.enums.SignUp('facebook'), 'facebook'), (modules.enums.SignUp('google-oauth2'), 'google-oauth2'), (modules.enums.SignUp('washmix'), 'washmix')], default='washmix', max_length=30, null=True)),
                ('fabric_softener', models.BooleanField(default=False)),
                ('fix_tears', models.BooleanField(default=False)),
                ('is_coupon', models.BooleanField(default=False)),
                ('package', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_list', to='core.Package')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
