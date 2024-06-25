import typing as t
import os

from celery import shared_task
from celery.worker.control import revoke
from datetime import datetime
from webpush import send_user_notification

from django.contrib.auth import get_user_model
from django.utils.timezone import timedelta

from apps.users.models import CoordimeetGroup
from apps.events.models import Event, EventCalendarTypeChoices


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
    def cancel_async_notification(task_id: str):
        revoke(task_id, terminate=True)

    @staticmethod
    @shared_task
    def _send_deadline_notification(event_id: int):
        event = Event.objects.get(id=event_id)
        
        # the date was selected; no action needed
        if event.selected_start_date and event.selected_end_date:
            return

        # send a notification to the organiser
        NotificationServices.send_user_notification(
            user=event.organiser,  # TODO: add admins
            head=f"The event response deadline is here!",
            body=f"{event} response period has ended. Pick a date!",
            url=event.frontend_url,
        )

    @staticmethod
    def send_deadline_notification(event: Event):
        return NotificationServices._send_deadline_notification.apply_async(
            args=[event.id],
            eta=event.deadline,
        )

    @staticmethod
    def __get_best_date_range(event: Event) -> t.List[t.Dict[str, t.Union[datetime, int]]]:
        """Return the best date range for an event. The same function as in Event.vue"""
        date_count_map = {}
        calendar_type = event.event_calendar_type

        for range in event.event_availability_options.all():
            current_date = range.start_date
            end_date = range.end_date

            while current_date <= end_date:
                date_string = current_date.isoformat()
                date_count_map[date_string] = date_count_map.get(date_string, 0) + 1
                current_date += timedelta(days=1) if calendar_type == EventCalendarTypeChoices.DATE else timedelta(hours=1)

        result = []
        date_count_keys = sorted(date_count_map.keys())

        for start_date in date_count_keys:
            end_date = datetime.fromisoformat(start_date) + timedelta(days=event.event_length) if calendar_type == EventCalendarTypeChoices.DATE else timedelta(hours=event.event_length)
            if end_date.isoformat() not in date_count_keys:
                continue

            hits = 0
            current_date = datetime.fromisoformat(start_date)
            while current_date < end_date:
                hits += date_count_map.get(current_date.isoformat(), 0)
                current_date += timedelta(days=1) if calendar_type == EventCalendarTypeChoices.DATE else timedelta(hours=1)

            result.append({
                "range": {
                    "start_date": datetime.fromisoformat(start_date),
                    "end_date": end_date,
                },
                "hits": hits,
            })
        
        # if there are no results, return the first available date
        if not result:
            first_range = event.event_availability_options.order_by("start_date").first()
            end_date = first_range.start_date + timedelta(days=event.event_length) if calendar_type == EventCalendarTypeChoices.DATE else timedelta(hours=event.event_length)
            return [{
                "range": {
                    "start_date": first_range.start_date,
                    "end_date": end_date,
                },
                "hits": 0,
            }]

        return sorted(result, key=lambda x: x["hits"], reverse=True)

    @staticmethod
    @shared_task
    def _send_event_finished_notification(event_id):
        event = Event.objects.get(id=event_id)
        
        # the date was selected; no action needed
        if event.selected_start_date and event.selected_end_date:
            return
        
        best_date_ranges = NotificationServices.__get_best_date_range(event)
        if not best_date_ranges:  # should not happen
            return

        best_range = best_date_ranges[0]
        event.selected_start_date = best_range["range"]["start_date"]
        event.selected_end_date = best_range["range"]["end_date"]
        event.save()

        # send a notification to the organiser
        NotificationServices.send_user_notification(
            user=event.organiser,  # TODO: add admins
            head=f"A date for your event was automatically selected!",
            body=f"The selected date for {event} is {event.get_formatted_selected_date}!",
            url=event.frontend_url,
        )

    @staticmethod
    def send_event_finished_notification(event: Event):
        """Send a notification at the first event's available_date."""

        first_available_date = event.event_availability_options.order_by("start_date").first().start_date
        return NotificationServices._send_event_finished_notification.apply_async(
            args=[event.id],
            eta=first_available_date,
        )