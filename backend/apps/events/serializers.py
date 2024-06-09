from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.events.models import Event, EventAvailabilityOption, EventNotification, EventParticipant, EventTypeChoices
from apps.users.models import CoordimeetGroup
from apps.users.serializers import UserSerializer, GroupSerializer, MemberSerializer


class EventAvailabilityOptionSerializer(serializers.ModelSerializer):
    """Serializer for the EventAvailabilityOption model"""

    class Meta:
        model = EventAvailabilityOption
        fields = ["start_date", "end_date"]


class EventNotificationSerializer(serializers.ModelSerializer):
    """Serializer for the EventNotification model"""

    class Meta:
        model = EventNotification
        fields = ["notification_type", "notification_time"]


class EventSerializer(serializers.ModelSerializer):
    """Serializer for the Event model"""

    event_availability_options = EventAvailabilityOptionSerializer(many=True)
    event_notifications = EventNotificationSerializer(many=True)
    organiser = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    invited_group = serializers.PrimaryKeyRelatedField(queryset=CoordimeetGroup.objects.all(), required=False)
    closed_group_users = UserSerializer(many=True, required=False)
    closed_group_members = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = "__all__"
    
    def create(self, validated_data):
        closed_group_users = validated_data.pop("closed_group_users")

        if validated_data.get("event_type") == EventTypeChoices.CLOSED:
            # create a new Group with is_closed=True
            # invite all users to the group
            group = CoordimeetGroup.objects.create(name=validated_data["title"], is_closed=True)
            # create members from the provided users (not all users are created already)
            for user_data in closed_group_users:
                user, _ = get_user_model().objects.get_or_create(**user_data)
                group.members.create(user=user)
            # add current user to event
            group.members.create(user=self.context["request"].user)
            validated_data["invited_group"] = group

        availability_options_data = validated_data.pop("event_availability_options")
        event_notifications_data = validated_data.pop("event_notifications")

        event = Event.objects.create(**validated_data)
        for availability_option_data in availability_options_data:
            EventAvailabilityOption.objects.create(event=event, **availability_option_data)

        for event_notification_data in event_notifications_data:
            EventNotification.objects.create(event=event, **event_notification_data)

        event.handle_notifications_create()
        return event

    def update(self, instance: Event, validated_data):
        closed_group_users = validated_data.pop("closed_group_users")

        if validated_data.get("event_type") == EventTypeChoices.CLOSED:
            # create a new Group with is_closed=True
            # invite all users to the group
            if instance.invited_group and instance.invited_group.is_closed:
                instance.invited_group.delete()

            group = CoordimeetGroup.objects.create(name=validated_data["title"], is_closed=True)
            # create members from the provided users (not all users are created already)
            for user_data in closed_group_users:
                user, _ = get_user_model().objects.get_or_create(**user_data)
                group.members.create(user=user)
            # add current user to event
            group.members.create(user=self.context["request"].user)
            validated_data["invited_group"] = group

        availability_options_data = validated_data.pop("event_availability_options")
        event_notifications_data = validated_data.pop("event_notifications")

        EventAvailabilityOption.objects.filter(event=instance).delete()
        for availability_option_data in availability_options_data:
            EventAvailabilityOption.objects.create(event=instance, **availability_option_data)

        EventNotification.objects.filter(event=instance).delete()
        for event_notification_data in event_notifications_data:
            EventNotification.objects.create(event=instance, **event_notification_data)

        event = super(EventSerializer, self).update(instance, validated_data)
        event.handle_notifications_update()
        return event

    def get_closed_group_members(self, instance):
        if instance.invited_group:
            return MemberSerializer(instance.invited_group.members.all(), many=True).data
        return []

    def to_representation(self, instance):
        self.fields["organiser"] = UserSerializer()
        self.fields["invited_group"] = GroupSerializer()

        return super(EventSerializer, self).to_representation(instance)


class EventParticipantSelectedSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventParticipant
        fields = ["email", "selected_ranges"]
    
    def to_representation(self, instance: EventParticipant):
        return {
            "first_name": instance.user.first_name,
            "last_name": instance.user.last_name,
            "email": instance.user.email,
            "not_comming": instance.not_comming,
            "selected_ranges": [
                {
                    "start_date": instance.start_date,
                    "end_date": instance.end_date,
                }
            ],
        }
