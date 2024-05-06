import os

from webpush.forms import WebPushForm, SubscriptionForm
from webpush.views import process_subscription_data

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request


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
