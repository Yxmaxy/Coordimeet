# Generated by Django 4.2 on 2024-07-28 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_remove_event_organiser_group_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventnotification',
            name='notification_type',
            field=models.IntegerField(choices=[(1, 'After creation'), (2, 'After update'), (3, 'Before deadline'), (4, 'After event date selected'), (5, 'Before event starts'), (6, 'At the deadline'), (7, 'Automatically finish event')]),
        ),
    ]
