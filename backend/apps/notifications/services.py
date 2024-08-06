import os

from celery import shared_task
from celery.worker.control import revoke
from datetime import datetime
from webpush import send_user_notification

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.users.models import CoordimeetGroup, MemberRole
from apps.events.services import EventServices


class NotificationServices:
    @staticmethod
    def send_user_notification(
        user: get_user_model(),
        head: str,
        body: str,
        url: str = None
    ):
        """Send a notification to a user."""

        icon_url = f"{os.environ.get('VITE_FRONTEND_URL')}/images/maskable_icon_x128.png"
        badge_url = f"{os.environ.get('VITE_FRONTEND_URL')}/images/maskable_icon_x96.png"

        payload = {
            "head": head,
            "body": body,
            "icon": icon_url,
            "badge": badge_url,
        }
        if url:
            payload["url"] = url

        send_user_notification(
            user=user,
            payload=payload,
            ttl=10000,
        )

        if settings.EMAIL_ENABLED:
            email_message = EmailMultiAlternatives(
                subject=f"[Coordimeet] {head}",
                body=body,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )
            email_message.attach_alternative(render_to_string("email.html", {"body": body}), "text/html")
            email_message.send(fail_silently=True)


    @staticmethod
    def send_group_notification(
        group: CoordimeetGroup,
        head: str,
        body: str,
        url: str = None
    ):
        """Send a notification to all members of a group."""
        for member in group.members.all():
            NotificationServices.send_user_notification(
                user=member.user,
                head=head,
                body=body,
                url=url,
            )

    @staticmethod
    def send_event_notification(
        event,
        head: str,
        body: str,
        url: str = None
    ):
        """
        If the event type is GROUP or CLOSED send a notification to all members.
        If the event type is PUBLIC send to all users who are in the event_participants
        """
        from apps.events.models import EventTypeChoices

        if event.event_type == EventTypeChoices.PUBLIC:
            for participant in event.event_participants.all():
                NotificationServices.send_user_notification(
                    user=participant.user,
                    head=head,
                    body=body,
                    url=url,
                )
            if not event.event_participants.filter(user=event.organiser).exists():
                NotificationServices.send_user_notification(
                    user=event.organiser,
                    head=head,
                    body=body,
                    url=url,
                )
        else:
            NotificationServices.send_group_notification(
                group=event.invited_group,
                head=head,
                body=body,
                url=url,
            )

    @staticmethod
    @shared_task
    def _send_async_event_notification(
        event_id: int,
        head: str,
        body: str,
        url: str = None
    ):
        from apps.events.models import Event
        event = Event.objects.get(id=event_id)
        NotificationServices.send_event_notification(event, head, body, url)

    @staticmethod
    def send_event_notification_at_time(
        event,
        head: str,
        body: str,
        time: datetime,
        url: str = None,
    ):
        """Send a notification to all members of a group at a specific time."""

        return NotificationServices._send_async_event_notification.apply_async(
            args=[event.id, head, body, url],
            eta=time,
        )

    @staticmethod
    @shared_task
    def _send_async_group_notification(
        group_id: int,
        head: str,
        body: str,
        url: str = None
    ):
        group = CoordimeetGroup.objects.get(id=group_id)
        NotificationServices.send_group_notification(group, head, body, url)

    @staticmethod
    def send_group_notification_at_time(
        group: CoordimeetGroup,
        head: str,
        body: str,
        time: datetime,
        url: str = None,
    ):
        """Send a notification to all members of a group at a specific time."""

        return NotificationServices._send_async_group_notification.apply_async(
            args=[group.id, head, body, url],
            eta=time,
        )

    @staticmethod
    def cancel_async_notification(task_id: str):
        revoke(task_id, terminate=True)

    @staticmethod
    @shared_task
    def _send_deadline_notification(event_id: int):
        from apps.events.models import Event
        event = Event.objects.get(id=event_id)
        
        # the date was selected; no action needed
        if event.selected_start_date and event.selected_end_date:
            return

        # send a notification to the organiser
        if not event.is_group_organiser:
            NotificationServices.send_user_notification(
                user=event.organiser,
                head=f"The event response deadline is here!",
                body=f"{event} response period has ended. Pick a date!",
                url=event.frontend_url,
            )
        else:
            for member in event.invited_group.members.filter(role__in=[MemberRole.OWNER, MemberRole.ADMIN]):
                NotificationServices.send_user_notification(
                    user=member.user,
                    head=f"The event response deadline is here!",
                    body=f"{event} response period has ended. Pick a date!",
                    url=event.frontend_url,
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
        from apps.events.models import Event
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
            for member in event.invited_group.members.filter(role__in=[MemberRole.OWNER, MemberRole.ADMIN]):
                NotificationServices.send_user_notification(
                    group=member.user,
                    head=f"A date for your event was automatically selected!",
                    body=f"The selected date for {event} is {event.get_formatted_selected_date}!",
                    url=event.frontend_url,
                )

    @staticmethod
    def send_event_finished_notification(event):
        """Send a notification at the first event's available_date."""

        first_available_date = event.event_availability_options.order_by("start_date").first().start_date
        return NotificationServices._send_event_finished_notification.apply_async(
            args=[event.id],
            eta=first_available_date,
        )