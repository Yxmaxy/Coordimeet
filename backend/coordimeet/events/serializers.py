from django.contrib.auth import get_user_model

from rest_framework import serializers

from coordimeet.events.models import Event, EventAvailabilityOption, EventParticipant, EventTypeChoices

from coordimeet.notifications.models import EventNotification
from coordimeet.notifications.services import EventNotificationServices

from coordimeet.users.models import CoordimeetGroup, CoordimeetUser
from coordimeet.users.serializers import CoordimeetUserSerializer, CoordimeetGroupSerializer, CoordimeetMemberSerializer
from coordimeet.users.services import CoordimeetUserServices


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

    def create(self, validated_data: dict):
        closed_group_users = validated_data.pop("closed_group_users")

        if validated_data.get("event_type") == EventTypeChoices.CLOSED:
            # create a new Group with is_closed=True
            # invite all users to the group
            group = CoordimeetGroup.objects.create(name=validated_data["title"], is_closed=True)
            # create members from the provided users (not all users are created already)
            for user_data in closed_group_users:
                coordimeet_user = CoordimeetUserServices.get_coordimeet_user(user_data["user"])
                group.coordimeet_members.create(coordimeet_user=coordimeet_user)
            # add current user to event
            coordimeet_user = CoordimeetUserServices.get_coordimeet_user(self.context["request"].user)
            group.coordimeet_members.create(coordimeet_user=coordimeet_user)
            validated_data["invited_group"] = group

        availability_options_data = validated_data.pop("event_availability_options")
        event_notifications_data = validated_data.pop("event_notifications")

        if not validated_data.get("is_group_organiser"):
            validated_data["organiser"] = CoordimeetUserServices.get_coordimeet_user(self.context["request"].user)

        event = Event.objects.create(**validated_data)
        for availability_option_data in availability_options_data:
            EventAvailabilityOption.objects.create(event=event, **availability_option_data)

        for event_notification_data in event_notifications_data:
            EventNotification.objects.create(event=event, **event_notification_data)

        EventNotificationServices.handle_notifications_create(event)
        return event

    def update(self, instance: Event, validated_data: dict):
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
                group.coordimeet_members.create(coordimeet_user=user)
            # add current user to event
            group.coordimeet_members.create(coordimeet_user=self.context["request"].user)
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
        EventNotificationServices.handle_notifications_update(event)
        return event

    def get_closed_group_members(self, instance: Event):
        if instance.invited_group:
            return CoordimeetMemberSerializer(instance.invited_group.coordimeet_members.all(), many=True).data
        return []

    def get_user_response(self, obj: Event):
        user = self.context["request"].user
        coordimeet_user = CoordimeetUserServices.get_coordimeet_user(user)

        if not coordimeet_user:
            return None
        try:
            participant = EventParticipant.objects.get(event=obj, coordimeet_user=coordimeet_user)
            return not participant.not_comming
        except EventParticipant.DoesNotExist:
            return None

    def to_representation(self, instance: Event):
        self.fields["organiser"] = CoordimeetUserSerializer()
        self.fields["invited_group"] = CoordimeetGroupSerializer()

        return super(EventSerializer, self).to_representation(instance)


class EventParticipantSelectedSerializer(serializers.ModelSerializer):
    participant_availabilities = EventAvailabilityOptionSerializer(many=True)
    coordimeet_user = CoordimeetUserSerializer()

    class Meta:
        model = EventParticipant
        fields = ["coordimeet_user", "not_comming", "participant_availabilities"]


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

        EventNotificationServices.handle_notifications_finished(instance)
        instance.refresh_from_db()
        return instance
