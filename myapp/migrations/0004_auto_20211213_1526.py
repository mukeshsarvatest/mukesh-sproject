# Generated by Django 3.0 on 2021-12-13 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='phone',
            new_name='mobile',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='phone',
            new_name='mobile',
        ),
    ]
