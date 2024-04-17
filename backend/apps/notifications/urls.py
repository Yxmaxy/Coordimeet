from django.urls import path, include

from apps.notifications import views


app_name = "notifications"
urlpatterns = [
    path("", include("webpush.urls")),
    path("send/", views.NotificationSendAPIView.as_view(), name="send_api"),
]
