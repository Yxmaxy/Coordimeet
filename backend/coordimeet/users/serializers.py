from rest_framework import serializers

from django.contrib.auth import get_user_model

from coordimeet.users.models import CoordimeetUser, CoordimeetGroup, CoordimeetMember, CoordimeetMemberRole


class CoordimeetUserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="username")
    is_anonymous = serializers.ReadOnlyField(source="is_anonymous")

    class Meta:
        model = CoordimeetUser
        fields = ["id", "username", "is_anonymous"]


class CoordimeetMemberSerializer(serializers.ModelSerializer):
    user = CoordimeetUserSerializer()

    class Meta:
        model = CoordimeetMember
        fields = ["id", "user", "role"]


class CoordimeetGroupSerializer(serializers.ModelSerializer):
    members = CoordimeetMemberSerializer(many=True)

    class Meta:
        model = CoordimeetGroup
        fields = ["id", "name", "members"]

    def create(self, validated_data: dict):
        members_data: list[dict] = validated_data.pop("members")

        # create group
        group = CoordimeetGroup.objects.create(**validated_data)

        # create and set the current user as the owner of the group
        CoordimeetMember.objects.create(
            user=self.context["request"].user,
            group=group,
            role=CoordimeetMemberRole.OWNER
        )

        # create all members
        # TODO: ?
        # for member_data in members_data:
        #     user_data = member_data.pop("user")
        #     user, _ = get_user_model().objects.get_or_create(**user_data)
        #     Member.objects.create(user=user, group=group, **member_data)

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
        instance.members.exclude(user__in=current_member_ids).exclude(role=CoordimeetMemberRole.OWNER).delete()

        return instance
