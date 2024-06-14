from django.urls import path

from apps.events import views


app_name = "events"
urlpatterns = [
    path("event/", views.EventOrganiserListCreateAPIView.as_view(), name="event_organiser_list_create_api"),
    path("event/invited/", views.EventInvitedListAPIView.as_view(), name="event_invited_list_api"),
    path("event/<str:event_uuid>/", views.EventManageAPIView.as_view(), name="event_manage_api"),
    path("event/participants/<str:event_uuid>/", views.EventParticipantAPIView.as_view(), name="event_participant_api"),
    path("event/organiser/<str:event_uuid>/", views.EventOrganiserAPIView.as_view(), name="event_organiser_api"),
]
