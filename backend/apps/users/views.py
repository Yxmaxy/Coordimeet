from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

from rest_framework_simplejwt.views import TokenObtainSlidingView
from rest_framework_simplejwt.exceptions import TokenError

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.users import serializers
from apps.users.models import CoordimeetGroup

from apps.utils.permissions import HasGroupOwnerOrAdminPermission, HasGroupOwnerPermission


class CustomTokenObtainSlidingView(TokenObtainSlidingView):
    serializer_class = serializers.CustomTokenObtainSlidingSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        email = request.data.get("email")
        user_with_email = get_user_model().objects.filter(email=email)
        
        if not user_with_email or not user_with_email[0].password:
            return Response({
                "error": "Your account was not found. You have to sign up first."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({"error": e.args[0]}, status=status.HTTP_401_UNAUTHORIZED)

        # set last login
        user = get_user_model().objects.get(id=serializer.validated_data["id"])
        user.last_login = timezone.now()
        user.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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
