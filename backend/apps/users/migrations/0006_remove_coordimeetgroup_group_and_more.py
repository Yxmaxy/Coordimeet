# Generated by Django 4.2 on 2024-05-17 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_group_uuid_coordimeetgroup_uuid_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coordimeetgroup',
            name='group',
        ),
        migrations.RemoveField(
            model_name='coordimeetgroup',
            name='webpush_group',
        ),
    ]
