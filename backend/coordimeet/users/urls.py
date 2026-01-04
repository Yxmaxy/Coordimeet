from django.urls import path

from coordimeet.users import views


app_name = "users"
urlpatterns = [
    path("current-user/", views.CurrentUserAPIView.as_view(), name="current_user_api"),
    path("anonymous/", views.AnonymousUserCreateAPIView.as_view(), name="anonymous_create_api"),
    path("group/", views.GroupListCreateAPIView.as_view(), name="group_api"),
    path("group/<int:pk>/", views.GroupRetrieveUpdateAPIView.as_view(), name="group_retrieve_update_api"),
    path("group/leave/<int:pk>/", views.GroupLeaveAPIView.as_view(), name="group_leave_api"),
    path("group/delete/<int:pk>/", views.GroupDestroyAPIView.as_view(), name="group_destroy_api"),
]
