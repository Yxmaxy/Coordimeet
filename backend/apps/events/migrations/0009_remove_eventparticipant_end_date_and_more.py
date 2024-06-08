# Generated by Django 4.2 on 2024-06-08 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_remove_eventparticipant_availability_level_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventparticipant',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='eventparticipant',
            name='start_date',
        ),
        migrations.CreateModel(
            name='EventParticipantAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participant_availabilities', to='events.eventparticipant')),
            ],
        ),
    ]
