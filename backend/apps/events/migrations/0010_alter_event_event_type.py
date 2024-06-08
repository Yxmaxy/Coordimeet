# Generated by Django 4.2 on 2024-06-08 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_remove_eventparticipant_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.IntegerField(choices=[(1, 'Public'), (2, 'Group'), (3, 'Closed')], default=1),
        ),
    ]
