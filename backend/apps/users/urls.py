from django.urls import path

from apps.users import views


app_name = "users"
urlpatterns = [
    path("token/", views.CustomTokenObtainSlidingView.as_view(), name="token_obtain_api"),
    path("user/<int:pk>/", views.UserAPIView.as_view(), name="user_api"),
]
