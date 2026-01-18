from django.urls import path

from coordimeet.friends.views import CoordimeetFriendListAPIView


urlpatterns = [
    path("list/", CoordimeetFriendListAPIView.as_view(), name="coordimeet_friend_list_api"),
]