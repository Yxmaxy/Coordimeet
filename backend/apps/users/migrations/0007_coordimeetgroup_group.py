# Generated by Django 4.2 on 2024-05-17 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0006_remove_coordimeetgroup_group_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordimeetgroup',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
        ),
    ]
