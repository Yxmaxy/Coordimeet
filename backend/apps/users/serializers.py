from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from django.utils import timezone

from apps.users.models import CoordimeetGroup, Member, MemberRole


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to include the user's data in the response.
    """

    def get_token(self, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # set last login
        self.user.last_login = timezone.now()
        self.user.save()

        return data


class UserSerializer(ModelSerializer):
    """
    Serializer for the user object.
    """

    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "email"]
        extra_kwargs = {
            "email": {
                "validators": [EmailValidator],
            },
        }


class UserCreateSerializer(ModelSerializer):
    """
    Serializer for creating the user object.
    """

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email", "password"]
        extra_kwargs = {
            "email": {
                "validators": [EmailValidator],
            },
            "password": {
                "write_only": True,
            },
        }

    def create(self, validated_data):
        """
        Creates a user. The following cases are possible:
        1. The user with this email doesn't exist yet -> create a new user.
        2. The user with this email exists and has logged in -> return None.
        3. the user with this email exists and has not logged in yet -> set the password and save the user.
        """
        email = validated_data.get("email")
        password = validated_data.get("password")

        try:
            user = get_user_model().objects.get(email=email)

            if user.last_login is None:  # Case 3
                user.set_password(password)
                user.save()
            else:  # Case 2
                return None

        except get_user_model().DoesNotExist:
            # Case 1
            user = get_user_model().objects.create_user(email=email, password=password)

        return user


class MemberSerializer(ModelSerializer):
    """
    Serializer for the member object.
    """

    user = UserSerializer()

    class Meta:
        model = Member
        fields = ["id", "user", "role"]


class GroupSerializer(ModelSerializer):
    """
    Serializer for the group object.
    """

    members = MemberSerializer(many=True)

    class Meta:
        model = CoordimeetGroup
        fields = ["id", "name", "members"]
    
    def create(self, validated_data):
        members_data = validated_data.pop("members")

        # create group
        group = CoordimeetGroup.objects.create(**validated_data)

        # create current user as the owner of the group
        Member.objects.create(user=self.context["request"].user, group=group, role=MemberRole.OWNER)

        # create all members
        for member_data in members_data:
            user_data = member_data.pop("user")
            user, _ = get_user_model().objects.get_or_create(**user_data)
            Member.objects.create(user=user, group=group, **member_data)

        return group

    def update(self, instance, validated_data):
        members_data = validated_data.pop("members")

        # update group
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        current_member_ids = []

        # update all still existing members
        for member_data in members_data:
            user_data = member_data.pop("user")
            user, created = get_user_model().objects.get_or_create(**user_data)
            if created:
                member = Member.objects.create(user=user, group=instance, **member_data)
            else:
                member, _ = instance.members.get_or_create(user=user)
            member.role = member_data.get("role", member.role)
            member.save()
            current_member_ids.append(member.user.id)
        
        # remove all members that are not in the new list
        instance.members.exclude(user__in=current_member_ids).exclude(role=MemberRole.OWNER).delete()

        return instance
