from django.urls import path, include

from coordimeet.notifications import views


app_name = "notifications"
urlpatterns = [
    path("save_information/", views.SaveInformationAPIView.as_view(), name="save_info"),
]
