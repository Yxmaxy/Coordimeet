from django.urls import path

from apps.events import views


app_name = "events"
urlpatterns = [
    path("event/", views.EventListCreateAPIView.as_view(), name="event_list_create_api"),
    path("event/<str:event_uuid>/", views.EventRetrieveUpdateDestroyAPIView.as_view(), name="event_retrieve_update_destroy_api"),
]
