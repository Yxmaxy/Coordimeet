# Generated by Django 4.2 on 2024-04-07 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_coordimeetgroup_alter_member_role_alter_member_group'),
        ('events', '0003_event_selected_end_date_event_selected_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='organiser_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organiser_group_events', to='users.coordimeetgroup'),
        ),
    ]
