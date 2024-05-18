from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainSlidingView

from django.contrib.auth import get_user_model

from apps.users import serializers
from apps.users.models import CoordimeetGroup

from apps.utils.permissions import HasGroupOwnerOrAdminPermission, HasGroupOwnerPermission


class CustomTokenObtainSlidingView(TokenObtainSlidingView):
    serializer_class = serializers.CustomTokenObtainSlidingSerializer
    # TODO: check that the user has last_login


class UserRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = "pk"


class UserCreateAPIView(APIView):
    def post(self, request):
        serializer = serializers.UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except Exception:
            return Response({"error": "User already exists"}, status=400)

        return Response(serializer.data, status=201)


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
    permission_classes = [IsAuthenticated, HasGroupOwnerOrAdminPermission]
    serializer_class = serializers.GroupSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return CoordimeetGroup.objects.filter(members__user=self.request.user)


class GroupDestroyAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated, HasGroupOwnerPermission]
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
