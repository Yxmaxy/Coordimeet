from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from django.utils.decorators import method_decorator

from coordimeet.users.models import CoordimeetUser
from coordimeet.users.serializers import CoordimeetUserSerializer
from coordimeet.users.decorators import with_coordimeet_user
from coordimeet.friends.models import CoordimeetFriend


@method_decorator(with_coordimeet_user, name="dispatch")
class CoordimeetFriendListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoordimeetUserSerializer

    def get_queryset(self):
        all_friends_user = CoordimeetFriend.objects.filter(user=self.request.coordimeet_user).values_list("friend", flat=True)
        all_friends_friend = CoordimeetFriend.objects.filter(friend=self.request.coordimeet_user).values_list("user", flat=True)

        all_friends = list(set(all_friends_user) | set(all_friends_friend))

        return CoordimeetUser.objects.filter(id__in=all_friends)
