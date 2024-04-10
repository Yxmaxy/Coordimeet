import uuid

from django.db import models
from django.contrib.auth import get_user_model

from apps.users.models import CoordimeetGroup


class EventTypeChoices(models.IntegerChoices):
    """Event types"""
    PUBLIC = 1, "Public"        # Anyone with the link can join
    GROUP = 2, "Group"          # Only group members can join


class EventCalendarTypeChoices(models.IntegerChoices):
    """Type of the calendar"""
    DATE = 1, "Date"
    DATE_HOUR = 2, "Date and hour"


class Event(models.Model):
    """Model for events"""

    title = models.CharField(max_length=255)
    event_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # the event_uuid is used to generate the invite link
    event_calendar_type = models.IntegerField(choices=EventCalendarTypeChoices.choices, default=EventCalendarTypeChoices.DATE_HOUR)
    event_type = models.IntegerField(choices=EventTypeChoices.choices, default=EventTypeChoices.PUBLIC)

    # set either the organiser or the organiser_group
    organiser = models.ForeignKey(get_user_model(), related_name="organiser_events", null=True, blank=True, on_delete=models.SET_NULL)
    organiser_group = models.ForeignKey(CoordimeetGroup, related_name="organiser_group_events", null=True, blank=True, on_delete=models.SET_NULL)

    invited_group = models.ForeignKey(CoordimeetGroup, related_name="invited_group_events", null=True, blank=True, on_delete=models.SET_NULL)

    description = models.TextField(null=True, blank=True)
    event_length = models.IntegerField()  # event length in units based on the event_calendar_type
    deadline = models.DateTimeField()

    selected_start_date = models.DateTimeField(null=True, blank=True)
    selected_end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Ensure that either organiser or organiser_group is set"""

        if self.organiser and self.organiser_group:
            raise ValueError("Event can't set both organiser and organiser_group")
        if not self.organiser and not self.organiser_group:
            raise ValueError("Event must set either organiser or organiser_group")
        super().save(*args, **kwargs)


class EventNotificationTypeChoices(models.IntegerChoices):
    """Choices for the notification types"""
    EMAIL = 1, "Email"
    PUSH = 2, "Push"


class EventNotification(models.Model):
    """Model for event notifications"""

    event = models.ForeignKey(Event, related_name="event_notifications", on_delete=models.CASCADE)
    notification_type = models.IntegerField(choices=EventNotificationTypeChoices.choices, default=EventNotificationTypeChoices.EMAIL)
    notification_time = models.DateTimeField()


class EventAvailabilityOption(models.Model):
    """Model for the date and time options which are available for the event."""

    event = models.ForeignKey(Event, related_name="event_availability_options", on_delete=models.CASCADE)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class EventParticipantAvailabilityLevelChoices(models.IntegerChoices):
    """Choices for the participant availability level"""
    IF_NEED_BE = 1, "If need be"
    MAYBE_AVAILABLE = 2, "Maybe available"
    AVAILABLE = 3, "Available"


class EventParticipant(models.Model):
    """
    Model for event participants.
    If the user is not logged in, the user_uuid is used to identify the user.
    """

    event = models.ForeignKey(Event, related_name="event_participants", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), related_name="user_events", null=True, blank=True, on_delete=models.SET_NULL)
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    availability_level = models.IntegerField(choices=EventParticipantAvailabilityLevelChoices.choices, default=EventParticipantAvailabilityLevelChoices.AVAILABLE)

    not_comming = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
