# Generated by Django 2.2.16 on 2020-10-16 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0002_set_foreign_keys"),
    ]

    operations = [
        migrations.RenameField(
            model_name="address", old_name="has_doormen", new_name="has_doorman",
        ),
    ]
