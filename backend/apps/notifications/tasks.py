from celery import shared_task

from apps.users.models import CoordimeetGroup
from apps.notifications.services import NotificationServices


@shared_task
def send_async_group_notification(group_id, head, body):
    group = CoordimeetGroup.objects.get(id=group_id)
    NotificationServices.send_group_notification(group, head, body)
    
