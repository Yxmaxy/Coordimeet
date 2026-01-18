import uuid

from django.db import models
from django.conf import settings

from coordimeet.users.models import CoordimeetUser, CoordimeetGroup


class EventTypeChoices(models.IntegerChoices):
    PUBLIC = 1, "Public"    # Anyone with the link can join
    GROUP = 2, "Group"      # Only group members can join
    CLOSED = 3, "Closed"    # Only invited users can join -> create "temp" group


class EventCalendarTypeChoices(models.IntegerChoices):
    DATE = 1, "Date"
    DATE_HOUR = 2, "Date and hour"


class Event(models.Model):
    title = models.CharField(max_length=255)
    event_uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Used to generate the invite link"
    )
    event_calendar_type = models.IntegerField(
        choices=EventCalendarTypeChoices.choices,
        default=EventCalendarTypeChoices.DATE_HOUR
    )
    event_type = models.IntegerField(
        choices=EventTypeChoices.choices,
        default=EventTypeChoices.PUBLIC
    )

    organiser = models.ForeignKey(
        CoordimeetUser,
        related_name="organiser_events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    invited_group = models.ForeignKey(
        CoordimeetGroup,
        related_name="invited_group_events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    is_group_organiser = models.BooleanField(default=False)

    description = models.TextField(null=True, blank=True)
    event_length = models.IntegerField(
        help_text="Event length in units based on the event_calendar_type"
    )
    deadline = models.DateTimeField()

    selected_start_date = models.DateTimeField(null=True, blank=True)
    selected_end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_formatted_selected_date(self) -> str:
        end_date = self.selected_end_date
        format_str = "%d. %m. %Y"
        if self.event_calendar_type == EventCalendarTypeChoices.DATE_HOUR:
            format_str = "%d. %m. %Y %H:%M"

        formatted_start = self.selected_start_date.strftime(format_str)
        formatted_end = end_date.strftime(format_str)

        if formatted_start == formatted_end:
            return f"at {formatted_start}"
        return f"from {formatted_start} to {formatted_end}"

    @property
    def frontend_url(self) -> str:
        return f"{settings.COORDIMEET_FRONTEND_URL}/event/{self.event_uuid}"

    def __str__(self):
        return self.title


class EventAvailabilityOption(models.Model):
    event = models.ForeignKey(
        Event,
        related_name="event_availability_options",
        on_delete=models.CASCADE
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class EventParticipant(models.Model):
    event = models.ForeignKey(
        Event,
        related_name="event_participants",
        on_delete=models.CASCADE
    )
    coordimeet_user = models.ForeignKey(
        CoordimeetUser,
        related_name="user_events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    not_comming = models.BooleanField(default=False)


class EventParticipantAvailability(models.Model):
    participant = models.ForeignKey(
        EventParticipant,
        related_name="participant_availabilities",
        on_delete=models.CASCADE
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
