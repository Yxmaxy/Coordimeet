from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainSlidingSerializer

from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator

from apps.users.models import CoordimeetGroup, Member, MemberRole


class CustomTokenObtainSlidingSerializer(TokenObtainSlidingSerializer):
     """
     Custom token serializer to include the `user_id` in the response.
     """
     def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        data["id"] = user.id

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
            current_member_ids.append(member.id)
        
        # remove all members that are not in the new list
        instance.members.exclude(user__in=current_member_ids).exclude(role=MemberRole.OWNER).delete()

        return instance
