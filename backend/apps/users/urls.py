from django.urls import path

from apps.users import views


app_name = "users"
urlpatterns = [
    path("token/", views.CustomTokenObtainSlidingView.as_view(), name="token_obtain_api"),
    path("user/", views.UserCreateAPIView.as_view(), name="user_create_api"),
    path("user/<int:pk>/", views.UserRetrieveAPIView.as_view(), name="user_manage_api"),
    path("user/exists/<str:email>/", views.UserExistsAPIView.as_view(), name="user_exists_api"),
    path("group/", views.GroupListCreateAPIView.as_view(), name="group_api"),
    path("group/<int:pk>/", views.GroupRetrieveUpdateAPIView.as_view(), name="group_retrieve_update_api"),
    path("group/leave/<int:pk>/", views.GroupLeaveAPIView.as_view(), name="group_leave_api"),
    path("group/delete/<int:pk>/", views.GroupDestroyAPIView.as_view(), name="group_destroy_api"),
]
