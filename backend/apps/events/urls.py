from django.urls import path

from apps.events import views


app_name = "events"
urlpatterns = [
    path("event/", views.EventListCreateAPIView.as_view(), name="event_api"),
]
