from django.urls import path, include

from apps.notifications import views


app_name = "notifications"
urlpatterns = [
    path("send/", views.NotificationSendAPIView.as_view(), name="send_api"),
    path("save_information/", views.SaveInformationAPIView.as_view(), name="save_info"),
]
