from django.contrib.auth import get_user_model

from rest_framework import serializers

from coordimeet.events.models import Event, EventAvailabilityOption, EventParticipant, EventTypeChoices
from coordimeet.notifications.models import EventNotification
from coordimeet.users.models import CoordimeetGroup
from coordimeet.users.serializers import CoordimeetUserSerializer, CoordimeetGroupSerializer, CoordimeetMemberSerializer


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
    closed_group_users = CoordimeetUserSerializer(many=True, required=False)
    closed_group_members = serializers.SerializerMethodField()

    user_response = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "title",
            "event_uuid",
            "event_calendar_type",
            "event_type",
            "organiser",
            "invited_group",
            "is_group_organiser",
            "description",
            "event_length",
            "deadline",
            "selected_start_date",
            "selected_end_date",
            "closed_group_users",
            "closed_group_members",
            "event_availability_options",
            "event_notifications",
            "user_response",
        ]
    
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
            return CoordimeetMemberSerializer(instance.invited_group.members.all(), many=True).data
        return []

    def get_user_response(self, obj):
        user = self.context["request"].user

        if not user.is_authenticated:
            return None
        try:
            participant = EventParticipant.objects.get(event=obj, user=user)
            return not participant.not_comming
        except EventParticipant.DoesNotExist:
            return None

    def to_representation(self, instance):
        self.fields["organiser"] = CoordimeetUserSerializer()
        self.fields["invited_group"] = CoordimeetGroupSerializer()

        return super(EventSerializer, self).to_representation(instance)


class EventParticipantSelectedSerializer(serializers.ModelSerializer):
    participant_availabilities = EventAvailabilityOptionSerializer(many=True)
    user = CoordimeetUserSerializer()

    class Meta:
        model = EventParticipant
        fields = ["user", "not_comming", "participant_availabilities"]


class EventFinishSerializer(serializers.ModelSerializer):
    event_notifications = EventNotificationSerializer(many=True)

    class Meta:
        model = Event
        fields = ["selected_start_date", "selected_end_date", "event_notifications"]

    def update(self, instance: Event, validated_data):
        event_notifications_data = validated_data.pop("event_notifications")
        super(EventFinishSerializer, self).update(instance, validated_data)

        for event_notification_data in event_notifications_data:
            EventNotification.objects.create(event=instance, **event_notification_data)
        
        instance.handle_notifications_finished()
        instance.refresh_from_db()
        return instance
