# Generated by Django 4.2 on 2024-05-12 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_delete_eventnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventnotification',
            name='task_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='eventnotification',
            unique_together={('event', 'notification_type')},
        ),
    ]
