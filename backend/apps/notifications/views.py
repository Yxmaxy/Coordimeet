import os
import json

from webpush import send_user_notification
from webpush.forms import WebPushForm, SubscriptionForm
from webpush.views import process_subscription_data

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from apps.users.models import CoordimeetGroup


class NotificationSendAPIView(APIView):
    parser_classes = [JSONParser]
    
    def post(self, request: Request):
        group_id = request.data.get("group_id")
        try:
            group = CoordimeetGroup.objects.get(id=group_id)
        except CoordimeetGroup.DoesNotExist:
            return Response({"message": "Invalid group id!"}, status=404)

        icon_url = f"{os.environ.get('VITE_FRONTEND_URL')}/images/maskable_icon_x128.png"

        payload = {
            "head": "Notification",
            "body": "Hello World",
            "icon": icon_url,
        }

        for member in group.members.all():
            send_user_notification(
                user=member.user,
                payload=payload,
                ttl=10000,
            )
        return Response({"message": "Notification sent!"})


class SaveInformationAPIView(APIView):
    """Modified from the `django-webpush` package to be compatible with DRF"""

    def post(self, request: Request):
        subscription_data = process_subscription_data(request.data)
        subscription_form = SubscriptionForm(subscription_data)
        web_push_form = WebPushForm(request.data)

        if subscription_form.is_valid() and web_push_form.is_valid():
            web_push_data = web_push_form.cleaned_data
            status_type = web_push_data.pop("status_type")

            if request.user.is_authenticated:
                subscription = subscription_form.get_or_save()
                web_push_form.save_or_delete(
                    subscription=subscription,
                    user=request.user,
                    status_type=status_type,
                    group_name=None,
                )

                # If subscribe is made, means object is created. So return 201
                if status_type == "subscribe":
                    return Response(status=201)
                # Unsubscribe is made, means object is deleted. So return 202
                elif "unsubscribe":
                    return Response(status=202)

        return Response(status=400)
