import os
import json

from webpush import send_notification_to_group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser

from apps.users.models import CoordimeetGroup


class NotificationSendAPIView(APIView):
    parser_classes = [JSONParser]
    
    def post(self, request):
        data = request.data
        group_id = data.get("group_id")
        try:
            group = CoordimeetGroup.objects.get(id=group_id)
        except CoordimeetGroup.DoesNotExist:
            return Response({"message": "Invalid group id!"}, status=404)

        # icon_url = f"{os.environ.get('VITE_FRONTEND_URL')}/images/maskable_icon_x128.png"

        payload = {
            "head": "Welcome!",
            "body": "Hello World",
            "url": "https://localhost/",
            "data": {"message": "hello there"}
        }
        
        send_notification_to_group(
            group_name=group.webpush_group.name,
            payload=json.dumps(payload),
            ttl=10000,
        )

        return Response({"message": "Notification sent!"})
