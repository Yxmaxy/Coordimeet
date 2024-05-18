from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainSlidingView

from django.contrib.auth import get_user_model

from apps.users import serializers
from apps.users.models import CoordimeetGroup


class CustomTokenObtainSlidingView(TokenObtainSlidingView):
    serializer_class = serializers.CustomTokenObtainSlidingSerializer


class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = "pk"


class UserExistsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, email):
        exists = get_user_model().objects.filter(email=email).exists()
        return Response({"exists": exists})


class GroupListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        return CoordimeetGroup.objects.filter(members__user=self.request.user)


class GroupRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]  # TODO: group admin or owner
    serializer_class = serializers.GroupSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return CoordimeetGroup.objects.filter(members__user=self.request.user)


class GroupDestroyAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated]  # TODO: group owner
    serializer_class = serializers.GroupSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return CoordimeetGroup.objects.filter(members__user=self.request.user)


class GroupLeaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        group = CoordimeetGroup.objects.get(pk=pk)
        group.members.filter(user=request.user).delete()
        return Response(status=204)
