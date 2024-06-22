import os
import uuid

from django.db import models
from django.contrib.auth import get_user_model

from apps.users.models import CoordimeetGroup
from apps.notifications.services import NotificationServices


class EventTypeChoices(models.IntegerChoices):
    """Event types"""
    PUBLIC = 1, "Public"        # Anyone with the link can join
    GROUP = 2, "Group"          # Only group members can join
    CLOSED = 3, "Closed"        # Only invited users can join -> create "temp" group


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

    organiser = models.ForeignKey(get_user_model(), related_name="organiser_events", null=True, blank=True, on_delete=models.SET_NULL)
    invited_group = models.ForeignKey(CoordimeetGroup, related_name="invited_group_events", null=True, blank=True, on_delete=models.SET_NULL)
    is_group_organiser = models.BooleanField(default=False)

    description = models.TextField(null=True, blank=True)
    event_length = models.IntegerField()  # event length in units based on the event_calendar_type
    deadline = models.DateTimeField()

    selected_start_date = models.DateTimeField(null=True, blank=True)
    selected_end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def send_notification_on_create(self) -> bool:
        return self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.CREATION
        ).exists()

    @property
    def send_notification_on_update(self) -> bool:
        return self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.UPDATE
        ).exists()

    @property
    def send_notification_date_selected(self) -> bool:
        return self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.EVENT_DATE_SELECT
        ).exists()

    @property
    def frontend_url(self) -> str:
        return f"{os.environ.get('VITE_FRONTEND_URL')}/event/{self.event_uuid}"

    def __str__(self):
        return self.title
    
    def handle_notifications_create(self):
        if not self.invited_group:
            return

        if self.send_notification_on_create:
            NotificationServices.send_group_notification(
                group=self.invited_group,
                head=f"New invitation!",
                body=f"You have been invited to participate in {self}",
                url=self.frontend_url,
            )
        
        # handle deadline
        if deadline_notifications := self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.DEADLINE
        ):
            notification = deadline_notifications.first()
            notification.task_id = NotificationServices.send_group_notification_at_time(
                group=self.invited_group,
                head=f"Event deadline!",
                body=f"{self} deadline is coming up!",
                time=notification.notification_time,
                url=self.frontend_url,
            ).id
            notification.save()

    def handle_notifications_update(self):
        if not self.invited_group:
            return

        if self.send_notification_on_update:
            NotificationServices.send_group_notification(
                group=self.invited_group,
                head=f"Event updated!",
                body=f"{self} has been updated, check it out!",
                url=self.frontend_url,
            )

        # handle deadline
        deadline_notifications = self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.DEADLINE
        )
        
        if deadline_notifications:
            # remove the extra notifications
            last_notification = deadline_notifications.last()
            for notification in deadline_notifications.exclude(id=last_notification.id):
                NotificationServices.cancel_async_notification(notification.task_id)
                notification.delete()

            last_notification.task_id = NotificationServices.send_group_notification_at_time(
                group=self.invited_group,
                head=f"Event deadline!",
                body=f"{self} deadline is coming up!",
                time=self.deadline,
                url=self.frontend_url,
            ).id
            last_notification.save()

    def handle_notifications_finished(self):
        if not self.invited_group:
            return

        # TODO: handle public groups

        # handle event date selected
        end_date = self.selected_end_date
        format_str = "%d. %m. %Y"
        if self.event_calendar_type == EventCalendarTypeChoices.DATE_HOUR:
            format_str = "%d. %m. %Y %H:%M"

        if self.send_notification_date_selected:
            NotificationServices.send_group_notification(
                group=self.invited_group,
                head=f"An event has finished!",
                body=f"{self} will take place from {self.selected_start_date.strftime(format_str)} to {end_date.strftime(format_str)}!",
                url=self.frontend_url,
            )
        
        # handle before event starts
        if start_notifications := self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.EVENT_START
        ):
            notification = start_notifications.first()
            notification.task_id = NotificationServices.send_group_notification_at_time(
                group=self.invited_group,
                head=f"Event is about to start!",
                body=f"{self} is starting soon!",
                time=notification.notification_time,
                url=self.frontend_url,
            ).id
            notification.save()


class EventNotificationTypeChoices(models.IntegerChoices):
    """Choices for the notification types"""
    CREATION = 1, "After creation"
    UPDATE = 2, "After update"
    DEADLINE = 3, "Before deadline"
    EVENT_DATE_SELECT = 4, "After event date selected"
    EVENT_START = 5, "Before event starts"


class EventNotification(models.Model):
    """Model for event notifications"""

    class Meta:
        unique_together = ["event", "notification_type"]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(Event, related_name="event_notifications", on_delete=models.CASCADE)
    notification_type = models.IntegerField(choices=EventNotificationTypeChoices.choices)
    notification_time = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)


class EventAvailabilityOption(models.Model):
    """Model for the date and time options which are available for the event."""

    event = models.ForeignKey(Event, related_name="event_availability_options", on_delete=models.CASCADE)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class EventParticipant(models.Model):
    """
    Model for event participants.
    """

    event = models.ForeignKey(Event, related_name="event_participants", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), related_name="user_events", null=True, blank=True, on_delete=models.SET_NULL)
    not_comming = models.BooleanField(default=False)


class EventParticipantAvailability(models.Model):
    """
    Model for the event participant availability.
    """

    participant = models.ForeignKey(EventParticipant, related_name="participant_availabilities", on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
