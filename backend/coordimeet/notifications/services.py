from celery import shared_task
from celery.worker.control import revoke
from datetime import datetime

from simple_notifications.services import NotificationService
from simple_notifications.models import PushSubscription

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from coordimeet.users.models import (
    CoordimeetUser,
    CoordimeetGroup,
    CoordimeetMemberRole,
)
from coordimeet.events.models import Event, EventTypeChoices
from coordimeet.events.services import EventServices
from coordimeet.notifications.models import EventNotificationTypeChoices



class NotificationUtilityServices:
    @staticmethod
    def send_user_notification(
        coordimeet_user: CoordimeetUser,
        title: str,
        body: str,
        **kwargs,
    ):
        if coordimeet_user.is_anonymous:
            return

        icon_url = (
            f"{settings.COORDIMEET_FRONTEND_URL}/images/maskable_icon_x128.png"
        )
        badge_url = (
            f"{settings.COORDIMEET_FRONTEND_URL}/images/maskable_icon_x96.png"
        )

        subscriptions = PushSubscription.objects.filter(
            user=coordimeet_user.user,
            app_name=settings.COORDIMEEET_NOTIFICATIONS_APP_NAME,
        )

        if subscriptions.exists():
            for subscription in subscriptions:
                NotificationService.send_push_notification(
                    subscription=subscription,
                    title=title,
                    body=body,
                    icon=icon_url,
                    badge=badge_url,
                    data=kwargs,
                )

        if settings.EMAIL_ENABLED:
            email_message = EmailMultiAlternatives(
                subject=f"[Coordimeet] {title}",
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=[coordimeet_user.user.email],
            )
            email_message.attach_alternative(
                render_to_string("email.html", {"body": body}), "text/html"
            )
            email_message.send(fail_silently=True)

    @staticmethod
    def send_group_notification(
        group: CoordimeetGroup, title: str, body: str, **kwargs,
    ):
        """Send a notification to all members of a group."""
        for member in group.coordimeet_members.all():
            NotificationUtilityServices.send_user_notification(
                coordimeet_user=member.coordimeet_user,
                title=title,
                body=body,
                **kwargs,
            )

    @staticmethod
    def send_event_notification(event: Event, head: str, body: str, **kwargs):
        """
        If the event type is GROUP or CLOSED send a notification to all members.
        If the event type is PUBLIC send to all users who are in the event_participants
        """
        if event.event_type == EventTypeChoices.PUBLIC:
            for participant in event.event_participants.all():
                NotificationUtilityServices.send_user_notification(
                    coordimeet_user=participant.coordimeet_user,
                    title=head,
                    body=body,
                    **kwargs,
                )
            if not event.event_participants.filter(coordimeet_user=event.organiser).exists():
                NotificationUtilityServices.send_user_notification(
                    coordimeet_user=event.organiser,
                    title=head,
                    body=body,
                    **kwargs,
                )
        else:
            NotificationUtilityServices.send_group_notification(
                group=event.invited_group,
                title=head,
                body=body,
                **kwargs,
            )

    @staticmethod
    @shared_task
    def _send_async_event_notification(
        event_id: int, title: str, body: str, **kwargs,
    ):
        event = Event.objects.get(id=event_id)
        NotificationUtilityServices.send_event_notification(event, title, body, **kwargs)

    @staticmethod
    def send_event_notification_at_time(
        event: Event,
        title: str,
        body: str,
        time: datetime,
        **kwargs,
    ):
        """Send a notification to all members of a group at a specific time."""

        return NotificationUtilityServices._send_async_event_notification.apply_async(
            args=[event.id, title, body],
            eta=time,
            kwargs=kwargs,
        )

    @staticmethod
    @shared_task
    def _send_async_group_notification(
        group_id: int, title: str, body: str
    ):
        group = CoordimeetGroup.objects.get(id=group_id)
        NotificationUtilityServices.send_group_notification(group, title, body)

    @staticmethod
    def send_group_notification_at_time(
        group: CoordimeetGroup,
        title: str,
        body: str,
        time: datetime,
    ):
        """Send a notification to all members of a group at a specific time."""

        return NotificationUtilityServices._send_async_group_notification.apply_async(
            args=[group.id, title, body],
            eta=time,
        )

    @staticmethod
    def cancel_async_notification(task_id: str):
        revoke(task_id, terminate=True)


class EventNotificationServices:
    @staticmethod
    def handle_notifications_create(event: Event):
        if not event.invited_group:
            return

        if event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.CREATION
        ).exists():
            NotificationUtilityServices.send_event_notification(
                event=event,
                head=f"New invitation!",
                body=f"You have been invited to participate in {event}",
                url=event.frontend_url,
            )
        
        # handle notification before deadline
        if deadline_notifications := event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.BEFORE_DEADLINE
        ):
            notification = deadline_notifications.first()
            notification.task_id = NotificationUtilityServices.send_group_notification_at_time(
                group=event.invited_group,
                head=f"Event deadline!",
                body=f"{event} deadline is coming up!",
                time=notification.notification_time,
                url=event.frontend_url,
            ).id
            notification.save()

        # handle notification at the deadline
        # notify the event's owner at the deadline, to pick a date
        event.event_notifications.create(
            notification_type=EventNotificationTypeChoices.DEADLINE,
            task_id=EventNotificationServices.send_deadline_notification(event=event).id
        )

        # handle notification for automatically finishing event
        # trigger this event at the first event's available_date
        event.event_notifications.create(
            notification_type=EventNotificationTypeChoices.FINISH_EVENT,
            task_id=EventNotificationServices.send_event_finished_notification(event=event).id
        )

    @staticmethod
    def handle_notifications_update(event: Event):
        if event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.UPDATE
        ).exists():
            NotificationUtilityServices.send_event_notification(
                event=event,
                head=f"Event updated!",
                body=f"{event} has been updated, check it out!",
                url=event.frontend_url,
            )

        if not event.invited_group:
            return

        # handle notification before deadline
        if deadline_notifications := event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.BEFORE_DEADLINE
        ):
            # remove the extra notifications
            last_notification = deadline_notifications.last()
            for notification in deadline_notifications.exclude(id=last_notification.id):
                NotificationUtilityServices.cancel_async_notification(notification.task_id)
                notification.delete()

            last_notification.task_id = NotificationUtilityServices.send_group_notification_at_time(
                group=event.invited_group,
                head=f"Event deadline!",
                body=f"{event} deadline is coming up!",
                time=event.deadline,
                url=event.frontend_url,
            ).id
            last_notification.save()

        # handle notification at the deadline
        # remove the previous deadline notification and create a new one
        if deadline_notification := event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.DEADLINE
        ).first():
            NotificationUtilityServices.cancel_async_notification(deadline_notification.task_id)
            deadline_notification.delete()
        event.event_notifications.create(
            notification_type=EventNotificationTypeChoices.DEADLINE,
            task_id=EventNotificationServices.send_deadline_notification(event=event).id
        )

        # handle notification for automatically finishing event
        # remove the previous notification and create a new one
        if finish_notification := event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.FINISH_EVENT
        ).first():
            NotificationUtilityServices.cancel_async_notification(finish_notification.task_id)
            finish_notification.delete()
        event.event_notifications.create(
            notification_type=EventNotificationTypeChoices.FINISH_EVENT,
            task_id=EventNotificationServices.send_event_finished_notification(event=event).id
        )

    @staticmethod
    def handle_notifications_finished(event: Event):
        if event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.EVENT_DATE_SELECT
        ).exists():
            NotificationUtilityServices.send_event_notification(
                event=event,
                head=f"An event has finished!",
                body=f"{event} will take place {event.get_formatted_selected_date}!",
                url=event.frontend_url,
            )
        
        # handle before event starts
        if start_notifications := event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.EVENT_START
        ):
            notification = start_notifications.first()
            notification.task_id = NotificationUtilityServices.send_event_notification_at_time(
                event=event,
                head=f"Event is about to start!",
                body=f"{event} is starting soon!",
                time=notification.notification_time,
                url=event.frontend_url,
            ).id
            notification.save()
    
    @staticmethod
    @shared_task
    def _send_deadline_notification(event_id: int):
        event = Event.objects.get(id=event_id)

        # the date was selected; no action needed
        if event.selected_start_date and event.selected_end_date:
            return

        # send a notification to the organiser
        if not event.is_group_organiser:
            NotificationUtilityServices.send_user_notification(
                coordimeet_user=event.organiser,
                title=f"The event response deadline is here!",
                body=f"{event} response period has ended. Pick a date!",
            )
        else:
            for member in event.invited_group.coordimeet_members.filter(
                role__in=[CoordimeetMemberRole.OWNER, CoordimeetMemberRole.ADMIN]
            ):
                NotificationUtilityServices.send_user_notification(
                    coordimeet_user=member.coordimeet_user,
                    title=f"The event response deadline is here!",
                    body=f"{event} response period has ended. Pick a date!",
                )

    @staticmethod
    def send_deadline_notification(event: Event):
        """Send a notification at the event's deadline."""
        return EventNotificationServices._send_deadline_notification.apply_async(
            args=[event.id],
            eta=event.deadline,
        )

    @staticmethod
    @shared_task
    def _send_event_finished_notification(event_id: int):
        event = Event.objects.get(id=event_id)

        # the date was selected; no action needed
        if event.selected_start_date and event.selected_end_date:
            return

        best_date_ranges = EventServices.get_best_date_range(event)
        if not best_date_ranges:  # should not happen
            return

        best_range = best_date_ranges[0]
        event.selected_start_date = best_range["range"]["start_date"]
        event.selected_end_date = best_range["range"]["end_date"]
        event.save()

        # send a notification to the organiser
        if not event.is_group_organiser:
            NotificationUtilityServices.send_user_notification(
                coordimeet_user=event.organiser,
                head=f"A date for your event was automatically selected!",
                body=f"The selected date for {event} is {event.get_formatted_selected_date}!",
                url=event.frontend_url,
            )
        else:
            for member in event.invited_group.coordimeet_members.filter(
                role__in=[CoordimeetMemberRole.OWNER, CoordimeetMemberRole.ADMIN]
            ):
                NotificationUtilityServices.send_user_notification(
                    coordimeet_user=member.coordimeet_user,
                    title=f"A date for your event was automatically selected!",
                    body=f"The selected date for {event} is {event.get_formatted_selected_date}!",
                    url=event.frontend_url,
                )

    @staticmethod
    def send_event_finished_notification(event: Event):
        """Send a notification at the first event's available_date."""

        first_available_date = (
            event.event_availability_options.order_by("start_date").first().start_date
        )
        return EventNotificationServices._send_event_finished_notification.apply_async(
            args=[event.id],
            eta=first_available_date,
        )
