from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Q

from coordimeet.users import serializers
from coordimeet.users.models import CoordimeetGroup, CoordimeetMemberRole
from coordimeet.users.services import CoordimeetUserServices

from coordimeet.events.permissions import HasGroupOwnerOrAdminPermission, HasGroupOwnerPermission


class CurrentUserAPIView(APIView):
    def get(self, request):
        coordimeet_user = CoordimeetUserServices.get_or_create_coordimeet_user_from_request(request)
        serializer = serializers.CoordimeetUserSerializer(coordimeet_user)
        response = Response(serializer.data)

        if coordimeet_user.is_anonymous and coordimeet_user.anonymous_username:
            CoordimeetUserServices.set_anonymous_user_cookie(response, coordimeet_user.anonymous_username)

        return response


class GroupListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CoordimeetGroupSerializer

    def get_queryset(self):
        # get the groups where is_closed is False and the user is a member and either a group owner or admin
        return CoordimeetGroup.objects.filter(
            Q(is_closed=False)
            & Q(coordimeet_members__coordimeet_user__user=self.request.user)
            & Q(coordimeet_members__role__in=[CoordimeetMemberRole.OWNER, CoordimeetMemberRole.ADMIN])
        ).distinct()


class GroupRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, HasGroupOwnerOrAdminPermission]
    serializer_class = serializers.CoordimeetGroupSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return CoordimeetGroup.objects.filter(coordimeet_members__coordimeet_user__user=self.request.user)


class GroupDestroyAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupOwnerPermission]
    serializer_class = serializers.CoordimeetGroupSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return CoordimeetGroup.objects.filter(coordimeet_members__coordimeet_user__user=self.request.user)


class GroupLeaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        group = CoordimeetGroup.objects.get(pk=pk)
        group.coordimeet_members.filter(coordimeet_user__user=self.request.user).delete()
        return Response(status=204)
