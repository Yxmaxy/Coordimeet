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
from coordimeet.events.services import EventServices


class NotificationServices:
    @staticmethod
    def send_user_notification(
        coordimeet_user: CoordimeetUser,
        title: str,
        body: str,
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
        group: CoordimeetGroup, title: str, body: str
    ):
        """Send a notification to all members of a group."""
        for member in group.members.all():
            NotificationServices.send_user_notification(
                coordimeet_user=member.user,
                title=title,
                body=body,
            )

    @staticmethod
    def send_event_notification(event, head: str, body: str):
        """
        If the event type is GROUP or CLOSED send a notification to all members.
        If the event type is PUBLIC send to all users who are in the event_participants
        """
        from coordimeet.events.models import EventTypeChoices

        if event.event_type == EventTypeChoices.PUBLIC:
            for participant in event.event_participants.all():
                NotificationServices.send_user_notification(
                    coordimeet_user=participant.user,
                    title=head,
                    body=body,
                )
            if not event.event_participants.filter(user=event.organiser).exists():
                NotificationServices.send_user_notification(
                    coordimeet_user=event.organiser,
                    title=head,
                    body=body,
                )
        else:
            NotificationServices.send_group_notification(
                group=event.invited_group,
                title=head,
                body=body,
            )

    @staticmethod
    @shared_task
    def _send_async_event_notification(
        event_id: int, title: str, body: str
    ):
        from coordimeet.events.models import Event

        event = Event.objects.get(id=event_id)
        NotificationServices.send_event_notification(event, title, body)

    @staticmethod
    def send_event_notification_at_time(
        event,
        title: str,
        body: str,
        time: datetime,
    ):
        """Send a notification to all members of a group at a specific time."""

        return NotificationServices._send_async_event_notification.apply_async(
            args=[event.id, title, body],
            eta=time,
        )

    @staticmethod
    @shared_task
    def _send_async_group_notification(
        group_id: int, title: str, body: str
    ):
        group = CoordimeetGroup.objects.get(id=group_id)
        NotificationServices.send_group_notification(group, title, body)

    @staticmethod
    def send_group_notification_at_time(
        group: CoordimeetGroup,
        title: str,
        body: str,
        time: datetime,
    ):
        """Send a notification to all members of a group at a specific time."""

        return NotificationServices._send_async_group_notification.apply_async(
            args=[group.id, title, body],
            eta=time,
        )

    @staticmethod
    def cancel_async_notification(task_id: str):
        revoke(task_id, terminate=True)

    @staticmethod
    @shared_task
    def _send_deadline_notification(event_id: int):
        from coordimeet.events.models import Event

        event = Event.objects.get(id=event_id)

        # the date was selected; no action needed
        if event.selected_start_date and event.selected_end_date:
            return

        # send a notification to the organiser
        if not event.is_group_organiser:
            NotificationServices.send_user_notification(
                coordimeet_user=event.organiser,
                title=f"The event response deadline is here!",
                body=f"{event} response period has ended. Pick a date!",
            )
        else:
            for member in event.invited_group.members.filter(
                role__in=[CoordimeetMemberRole.OWNER, CoordimeetMemberRole.ADMIN]
            ):
                NotificationServices.send_user_notification(
                    user=member.user,
                    title=f"The event response deadline is here!",
                    body=f"{event} response period has ended. Pick a date!",
                )

    @staticmethod
    def send_deadline_notification(event):
        return NotificationServices._send_deadline_notification.apply_async(
            args=[event.id],
            eta=event.deadline,
        )

    @staticmethod
    @shared_task
    def _send_event_finished_notification(event_id):
        from coordimeet.events.models import Event

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
            NotificationServices.send_user_notification(
                user=event.organiser,
                head=f"A date for your event was automatically selected!",
                body=f"The selected date for {event} is {event.get_formatted_selected_date}!",
                url=event.frontend_url,
            )
        else:
            for member in event.invited_group.members.filter(
                role__in=[CoordimeetMemberRole.OWNER, CoordimeetMemberRole.ADMIN]
            ):
                NotificationServices.send_user_notification(
                    group=member.user,
                    head=f"A date for your event was automatically selected!",
                    body=f"The selected date for {event} is {event.get_formatted_selected_date}!",
                    url=event.frontend_url,
                )

    @staticmethod
    def send_event_finished_notification(event):
        """Send a notification at the first event's available_date."""

        first_available_date = (
            event.event_availability_options.order_by("start_date").first().start_date
        )
        return NotificationServices._send_event_finished_notification.apply_async(
            args=[event.id],
            eta=first_available_date,
        )


class EventNotificationServices:
        def handle_notifications_create(self):
        if not self.invited_group:
            return

        if self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.CREATION
        ).exists():
            NotificationServices.send_event_notification(
                event=self,
                head=f"New invitation!",
                body=f"You have been invited to participate in {self}",
                url=self.frontend_url,
            )
        
        # handle notification before deadline
        if deadline_notifications := self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.BEFORE_DEADLINE
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

        # handle notification at the deadline
        # notify the event's owner at the deadline, to pick a date
        self.event_notifications.create(
            notification_type=EventNotificationTypeChoices.DEADLINE,
            task_id=NotificationServices.send_deadline_notification(event=self).id
        )

        # handle notification for automatically finishing event
        # trigger this event at the first event's available_date
        self.event_notifications.create(
            notification_type=EventNotificationTypeChoices.FINISH_EVENT,
            task_id=NotificationServices.send_event_finished_notification(event=self).id
        )

    def handle_notifications_update(self):
        if self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.UPDATE
        ).exists():
            NotificationServices.send_event_notification(
                event=self,
                head=f"Event updated!",
                body=f"{self} has been updated, check it out!",
                url=self.frontend_url,
            )

        if not self.invited_group:
            return

        # handle notification before deadline
        if deadline_notifications := self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.BEFORE_DEADLINE
        ):
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

        # handle notification at the deadline
        # remove the previous deadline notification and create a new one
        if deadline_notification := self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.DEADLINE
        ).first():
            NotificationServices.cancel_async_notification(deadline_notification.task_id)
            deadline_notification.delete()
        self.event_notifications.create(
            notification_type=EventNotificationTypeChoices.DEADLINE,
            task_id=NotificationServices.send_deadline_notification(event=self).id
        )

        # handle notification for automatically finishing event
        # remove the previous notification and create a new one
        if finish_notification := self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.FINISH_EVENT
        ).first():
            NotificationServices.cancel_async_notification(finish_notification.task_id)
            finish_notification.delete()
        self.event_notifications.create(
            notification_type=EventNotificationTypeChoices.FINISH_EVENT,
            task_id=NotificationServices.send_event_finished_notification(event=self).id
        )

    def handle_notifications_finished(self):
        if self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.EVENT_DATE_SELECT
        ).exists():
            NotificationServices.send_event_notification(
                event=self,
                head=f"An event has finished!",
                body=f"{self} will take place {self.get_formatted_selected_date}!",
                url=self.frontend_url,
            )
        
        # handle before event starts
        if start_notifications := self.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.EVENT_START
        ):
            notification = start_notifications.first()
            notification.task_id = NotificationServices.send_event_notification_at_time(
                event=self,
                head=f"Event is about to start!",
                body=f"{self} is starting soon!",
                time=notification.notification_time,
                url=self.frontend_url,
            ).id
            notification.save()