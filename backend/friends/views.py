from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User

from friends.models import Friend
from friends.serializers import UserSerializer


class FriendListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        all_friends_user = Friend.objects.filter(user=self.request.user).values_list("friend", flat=True)
        all_friends_friend = Friend.objects.filter(friend=self.request.user).values_list("user", flat=True)

        all_friends = list(set(all_friends_user) | set(all_friends_friend))

        return User.objects.filter(id__in=all_friends)
