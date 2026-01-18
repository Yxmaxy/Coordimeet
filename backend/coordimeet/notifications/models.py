import uuid

from django.db import models

from coordimeet.events.models import Event


class EventNotificationTypeChoices(models.IntegerChoices):
    CREATION = 1, "After creation"
    UPDATE = 2, "After update"
    BEFORE_DEADLINE = 3, "Before deadline"
    EVENT_DATE_SELECT = 4, "After event date selected"
    EVENT_START = 5, "Before event starts"
    DEADLINE = 6, "At the deadline"
    FINISH_EVENT = 7, "Automatically finish event"


class EventNotification(models.Model):
    class Meta:
        unique_together = ["event", "notification_type"]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(
        Event,
        related_name="event_notifications",
        on_delete=models.CASCADE
    )
    notification_type = models.IntegerField(
        choices=EventNotificationTypeChoices.choices
    )
    notification_time = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
