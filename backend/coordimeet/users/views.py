from wonderwords import RandomWord

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Q
from django.contrib.auth import get_user_model

from coordimeet.users import serializers
from coordimeet.users.models import CoordimeetGroup, UserTypes, MemberRole

from coordimeet.events.permissions import HasGroupOwnerOrAdminPermission, HasGroupOwnerPermission


class CustomTokenObtainView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainSerializer


class UserCreateAPIView(APIView):
    def post(self, request):
        serializer = serializers.UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except Exception:
            return Response({"error": "User already exists"}, status=400)

        return Response(serializer.data, status=201)


class AnonymousUserCreateAPIView(APIView):
    def post(self, request):
        r = RandomWord()
        limit = 100

        # try to create a user with a random username
        while limit > 0:
            try:
                random_adjective = r.word(include_parts_of_speech=["adjectives"])
                random_noun = r.word(include_parts_of_speech=["nouns"])
                email = f"{random_adjective}.{random_noun}@coordimeet.eu"
                user = get_user_model().objects.create(
                    email=email,
                    user_type=UserTypes.ANONYMOUS,
                )
                break
            except get_user_model().DoesNotExist:
                pass
        
        # generate a token with additional data
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["first_name"] = user.first_name
        refresh["last_name"] = user.last_name
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=201)


class UserExistsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, email):
        exists = get_user_model().objects.filter(email=email).exists()
        return Response({"exists": exists})


class GroupListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        # get the groups where is_closed is False and the user is a member and either a group owner or admin
        return CoordimeetGroup.objects.filter(
            Q(is_closed=False)
            & Q(members__user=self.request.user)
            & Q(members__role__in=[MemberRole.OWNER, MemberRole.ADMIN])
        )


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
