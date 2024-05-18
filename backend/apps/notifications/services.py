import os
from celery import shared_task
from celery.worker.control import revoke
from datetime import datetime

from webpush import send_user_notification

from apps.users.models import CoordimeetGroup


class NotificationServices:
    @staticmethod
    def send_group_notification(
        group: CoordimeetGroup,
        head: str,
        body: str,
        url: str = None
    ):
        """Send a notification to all members of a group."""

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

        for member in group.members.all():
            send_user_notification(
                user=member.user,
                payload=payload,
                ttl=10000,
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
