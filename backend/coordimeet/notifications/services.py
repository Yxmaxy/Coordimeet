import uuid
from celery import shared_task
from celery.worker.control import revoke
from datetime import datetime

from simple_notifications.services import NotificationService, NotificationSubscriptionService

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from coordimeet.users.models import (
    CoordimeetUser,
    CoordimeetGroup,
    CoordimeetMemberRole,
)
from coordimeet.events.models import Event, EventTypeChoices, EventNotificationMethodChoices
from coordimeet.events.services import EventServices
from coordimeet.notifications.models import EventNotificationTypeChoices


class NotificationUtilityServices:
    @staticmethod
    def get_email_domain() -> str:
        return settings.EMAIL_HOST_USER.split("@")[-1]

    @staticmethod
    def _generate_email_message_id() -> str:
        """
        Generate a unique Message-ID for an email using a random UUID.
        
        Format: <random_uuid@domain>
        """
        domain = NotificationUtilityServices.get_email_domain()
        return f"<{uuid.uuid4().hex}@{domain}>"

    @staticmethod
    def _create_threaded_email(
        subject: str,
        body: str,
        html_body: str,
        to_email: str,
        event: Event,
    ) -> EmailMultiAlternatives:
        """
        Create an email message with proper threading headers.
        
        Email threading is achieved by:
        1. Generating a unique random Message-ID for this email
        2. Setting In-Reply-To to the most recent message in the thread
        3. Setting References to all previous messages in the thread
        4. Storing the new Message-ID in the event for future emails
        
        Args:
            subject: Email subject line
            body: Plain text body
            html_body: HTML body
            to_email: Recipient email address
            event: Event object (used for threading context and storing message IDs)
        
        Returns:
            EmailMultiAlternatives object with threading headers set
        """
        message_id = NotificationUtilityServices._generate_email_message_id()

        previous_message_ids = event.email_thread_message_ids or []

        headers = {
            "Message-ID": message_id,
        }

        if previous_message_ids:
            headers["In-Reply-To"] = previous_message_ids[-1]
            headers["References"] = " ".join(previous_message_ids)

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
            headers=headers,
        )

        email_message.attach_alternative(html_body, "text/html")

        # store the new Message-ID in the event for future threading
        event.email_thread_message_ids.append(message_id)
        event.save(update_fields=["email_thread_message_ids"])

        return email_message

    @staticmethod
    def send_user_notification(
        coordimeet_user: CoordimeetUser,
        title: str,
        body: str,
        event: Event,
        data: dict = None,
    ):
        icon_url = f"{settings.COORDIMEET_FRONTEND_URL}/images/maskable_icon_x128.png"
        badge_url = f"{settings.COORDIMEET_FRONTEND_URL}/images/maskable_icon_x96.png"

        data = data or {}
        event_url = data.get("url", None)

        # send push notification if method is PUSH or BOTH
        if event.notification_method in [EventNotificationMethodChoices.PUSH, EventNotificationMethodChoices.BOTH]:
            subscriptions = NotificationSubscriptionService.get_user_subscriptions(coordimeet_user)
            for subscription in subscriptions:
                NotificationService.send_push_notification(
                    subscription=subscription,
                    title=title,
                    body=body,
                    icon=icon_url,
                    badge=badge_url,
                    data=data,
                )

        # send email notification if method is EMAIL or BOTH
        if event.notification_method in [EventNotificationMethodChoices.EMAIL, EventNotificationMethodChoices.BOTH]:
            if settings.EMAIL_ENABLED and not coordimeet_user.is_anonymous:
                logo_url = f"{settings.COORDIMEET_FRONTEND_URL}/images/logo.png"
                html_body = render_to_string("email.html", {
                    "title": title,
                    "body": body,
                    "logo_url": logo_url,
                    "event_url": event_url,
                })

                NotificationUtilityServices.send_email_notification(
                    subject=f"[Coordimeet] {title}",
                    body=body,
                    html_body=html_body,
                    to_email=coordimeet_user.email,
                    event=event,
                )

    @staticmethod
    @shared_task
    def _send_email_notification(
        subject: str,
        body: str,
        html_body: str,
        to_email: str,
        event_id: int,
    ):
        event = Event.objects.get(id=event_id)
        email_message = NotificationUtilityServices._create_threaded_email(
            subject=subject,
            body=body,
            html_body=html_body,
            to_email=to_email,
            event=event,
        )
        email_message.send(fail_silently=True)

    @staticmethod
    def send_email_notification(
        subject: str,
        body: str,
        html_body: str,
        to_email: str,
        event: Event,
    ):
        return NotificationUtilityServices._send_email_notification.delay(
            subject=subject,
            body=body,
            html_body=html_body,
            to_email=to_email,
            event_id=event.id,
        )

    @staticmethod
    def send_group_notification(
        group: CoordimeetGroup,
        title: str,
        body: str,
        event: Event,
        data: dict = None,
    ):
        """Send a notification to all members of a group."""
        for member in group.coordimeet_members.all():
            NotificationUtilityServices.send_user_notification(
                coordimeet_user=member.coordimeet_user,
                title=title,
                body=body,
                event=event,
                data=data or {},
            )

    @staticmethod
    def send_event_notification(
        event: Event,
        title: str,
        body: str,
        data: dict = None,
    ):
        """
        If the event type is GROUP or CLOSED send a notification to all members.
        If the event type is PUBLIC send to all users who are in the event_participants
        """
        if event.event_type == EventTypeChoices.PUBLIC:
            for participant in event.event_participants.all():
                NotificationUtilityServices.send_user_notification(
                    coordimeet_user=participant.coordimeet_user,
                    title=title,
                    body=body,
                    event=event,
                    data=data or {},
                )
            if not event.event_participants.filter(coordimeet_user=event.organiser).exists():
                NotificationUtilityServices.send_user_notification(
                    coordimeet_user=event.organiser,
                    title=title,
                    body=body,
                    event=event,
                    data=data or {},
                )
        else:
            NotificationUtilityServices.send_group_notification(
                group=event.invited_group,
                title=title,
                body=body,
                event=event,
                data=data or {},
            )

    @staticmethod
    @shared_task
    def _send_async_event_notification(
        event_id: int,
        title: str,
        body: str,
        data: dict = None,
    ):
        event = Event.objects.get(id=event_id)
        NotificationUtilityServices.send_event_notification(
            event=event,
            title=title,
            body=body,
            data=data or {},
        )

    @staticmethod
    def send_event_notification_at_time(
        event: Event,
        title: str,
        body: str,
        time: datetime,
        data: dict,
    ):
        """Send a notification to all members of a group at a specific time."""

        return NotificationUtilityServices._send_async_event_notification.apply_async(
            args=[event.id, title, body, data],
            eta=time,
        )

    @staticmethod
    @shared_task
    def _send_async_group_notification(
        group_id: int,
        title: str,
        body: str,
        event_id: int,
        data: dict = None,
    ):
        group = CoordimeetGroup.objects.get(id=group_id)
        event = Event.objects.get(id=event_id) if event_id else None
        NotificationUtilityServices.send_group_notification(
            group=group,
            title=title,
            body=body,
            event=event,
            data=data or {},
        )

    @staticmethod
    def send_group_notification_at_time(
        group: CoordimeetGroup,
        title: str,
        body: str,
        time: datetime,
        event: Event,
        data: dict = None,
    ):
        """Send a notification to all members of a group at a specific time."""

        return NotificationUtilityServices._send_async_group_notification.apply_async(
            args=[group.id, title, body, event.id, data or {}],
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
                title=f"New invitation!",
                body=f"You have been invited to participate in {event}",
                data={"url": event.frontend_url},
            )
        
        # handle notification before deadline
        if deadline_notifications := event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.BEFORE_DEADLINE
        ):
            notification = deadline_notifications.first()
            notification.task_id = NotificationUtilityServices.send_group_notification_at_time(
                group=event.invited_group,
                title=f"Event deadline!",
                body=f"{event} deadline is coming up!",
                time=notification.notification_time,
                event=event,
                data={"url": event.frontend_url},
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
                title=f"Event updated!",
                body=f"{event} has been updated, check it out!",
                data={"url": event.frontend_url},
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
                title=f"Event deadline!",
                body=f"{event} deadline is coming up!",
                time=last_notification.notification_time,
                event=event,
                data={"url": event.frontend_url},
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
                title=f"An event has finished!",
                body=f"{event} will take place {event.get_formatted_selected_date}!",
                data={"url": event.frontend_url},
            )
        
        # handle before event starts
        if start_notifications := event.event_notifications.filter(
            notification_type=EventNotificationTypeChoices.EVENT_START
        ):
            notification = start_notifications.first()
            notification.task_id = NotificationUtilityServices.send_event_notification_at_time(
                event=event,
                title=f"Event is about to start!",
                body=f"{event} is starting soon!",
                time=notification.notification_time,
                data={"url": event.frontend_url},
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
                event=event,
                data={"url": event.frontend_url},
            )
        else:
            for member in event.invited_group.coordimeet_members.filter(
                role__in=[CoordimeetMemberRole.OWNER, CoordimeetMemberRole.ADMIN]
            ):
                NotificationUtilityServices.send_user_notification(
                    coordimeet_user=member.coordimeet_user,
                    title=f"The event response deadline is here!",
                    body=f"{event} response period has ended. Pick a date!",
                    event=event,
                    data={"url": event.frontend_url},
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
                title=f"A date for your event was automatically selected!",
                body=f"The selected date for {event} is {event.get_formatted_selected_date}!",
                event=event,
                data={"url": event.frontend_url},
            )
        else:
            for member in event.invited_group.coordimeet_members.filter(
                role__in=[CoordimeetMemberRole.OWNER, CoordimeetMemberRole.ADMIN]
            ):
                NotificationUtilityServices.send_user_notification(
                    coordimeet_user=member.coordimeet_user,
                    title=f"A date for your event was automatically selected!",
                    body=f"The selected date for {event} is {event.get_formatted_selected_date}!",
                    event=event,
                    data={"url": event.frontend_url},
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
