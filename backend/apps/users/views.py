from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainSlidingView

from django.contrib.auth import get_user_model

from apps.users import serializers


class CustomTokenObtainSlidingView(TokenObtainSlidingView):
    serializer_class = serializers.CustomTokenObtainSlidingSerializer


class UserAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = "pk"
