from rest_framework import serializers

from django.contrib.auth import get_user_model

from coordimeet.users.models import CoordimeetUser, CoordimeetGroup, CoordimeetMember, CoordimeetMemberRole
from coordimeet.users.services import CoordimeetUserServices


class CoordimeetUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    class Meta:
        model = CoordimeetUser
        fields = ["id", "user", "email", "is_anonymous"]


class CoordimeetMemberSerializer(serializers.ModelSerializer):
    coordimeet_user = CoordimeetUserSerializer()

    class Meta:
        model = CoordimeetMember
        fields = ["id", "coordimeet_user", "role"]


class CoordimeetGroupSerializer(serializers.ModelSerializer):
    coordimeet_members = CoordimeetMemberSerializer(many=True)

    class Meta:
        model = CoordimeetGroup
        fields = ["id", "name", "coordimeet_members"]

    def create(self, validated_data: dict):
        coordimeet_members_data: list[dict] = validated_data.pop("coordimeet_members")

        # create group
        group = CoordimeetGroup.objects.create(**validated_data)

        # create and set the current user as the owner of the group
        coordimeet_user = CoordimeetUserServices.get_or_create_authenticated_coordimeet_user(self.context["request"].user)
        CoordimeetMember.objects.create(
            coordimeet_user=coordimeet_user,
            coordimeet_group=group,
            role=CoordimeetMemberRole.OWNER
        )

        # create all members
        for member_data in coordimeet_members_data:
            user_data = member_data.pop("coordimeet_user")

            coordimeet_user = CoordimeetUserServices.get_or_create_authenticated_coordimeet_user(user_data["user"])
            CoordimeetMember.objects.create(coordimeet_user=coordimeet_user, coordimeet_group=group, **member_data)

        return group

    def update(self, instance: CoordimeetGroup, validated_data: dict):
        coordimeet_members_data = validated_data.pop("coordimeet_members")

        # update group
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        current_member_ids = []

        # update all still existing members
        for member_data in coordimeet_members_data:
            user_data = member_data.pop("coordimeet_user")

            coordimeet_user = CoordimeetUserServices.get_or_create_authenticated_coordimeet_user(user_data["user"])
            member, _ = instance.coordimeet_members.update_or_create(coordimeet_user=coordimeet_user, defaults=member_data)
            current_member_ids.append(member.coordimeet_user.id)

        # remove all members that are not in the new list
        instance.coordimeet_members.exclude(coordimeet_user__in=current_member_ids).exclude(role=CoordimeetMemberRole.OWNER).delete()

        return instance
