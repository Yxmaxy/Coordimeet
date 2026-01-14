from django.urls import path

from coordimeet.events import views


app_name = "events"
urlpatterns = [
    path("event/", views.EventOrganiserListAPIView.as_view(), name="event_organiser_list_api"),
    path("event/", views.EventOrganiserCreateAPIView.as_view(), name="event_organiser_create_api"),
    path("event/invited/", views.EventInvitedListAPIView.as_view(), name="event_invited_list_api"),
    path("event/<str:event_uuid>/", views.EventManageAPIView.as_view(), name="event_manage_api"),
    path("event/participants/<str:event_uuid>/", views.EventParticipantAPIView.as_view(), name="event_participant_api"),
    path("event/organiser/<str:event_uuid>/", views.EventOrganiserAPIView.as_view(), name="event_organiser_api"),
    path("event/icalendar/<str:event_uuid>/", views.EventICalendarAPIView.as_view(), name="event_icalendar_api"),
]
