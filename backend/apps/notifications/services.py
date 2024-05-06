import os
from datetime import datetime

from webpush import send_user_notification

from apps.users.models import CoordimeetGroup
from apps.notifications.tasks import send_async_group_notification

class NotificationServices:
    @staticmethod
    def send_group_notification(group: CoordimeetGroup, head: str, body: str):
        """Send a notification to all members of a group."""

        icon_url = f"{os.environ.get('VITE_FRONTEND_URL')}/images/maskable_icon_x128.png"

        payload = {
            "head": head,
            "body": body,
            "icon": icon_url,
        }

        for member in group.members.all():
            send_user_notification(
                user=member.user,
                payload=payload,
                ttl=10000,
            )

    @staticmethod
    def send_group_notification_at_time(group: CoordimeetGroup, head: str, body: str, time: datetime):
        """Send a notification to all members of a group at a specific time."""

        send_async_group_notification.apply_async(
            args=[group.id, head, body],
            eta=time,
        )
