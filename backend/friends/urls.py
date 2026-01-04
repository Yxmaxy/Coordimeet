from django.urls import path

from friends.views import FriendListAPIView


urlpatterns = [
    path("list/", FriendListAPIView.as_view(), name="friend_list_api"),
]