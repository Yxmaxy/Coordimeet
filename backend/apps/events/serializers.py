from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.events.models import Event, EventAvailabilityOption, EventNotification
from apps.users.models import CoordimeetGroup
from apps.users.serializers import UserSerializer


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

    class Meta:
        model = Event
        fields = "__all__"
    
    def create(self, validated_data):
        availability_options_data = validated_data.pop("event_availability_options")
        event_notifications_data = validated_data.pop("event_notifications")

        event = Event.objects.create(**validated_data)
        for availability_option_data in availability_options_data:
            EventAvailabilityOption.objects.create(event=event, **availability_option_data)

        for event_notification_data in event_notifications_data:
            EventNotification.objects.create(event=event, **event_notification_data)

        event.handle_notifications_create()

        return event

    # TODO: update
    # def update(self, instance, validated_data):
    #     availability_options_data = validated_data.pop("event_availability_options")
    #     event_notifications_data = validated_data.pop("event_notifications")

    #     instance = super(EventSerializer, self).update(instance, validated_data)

    #     # handle notifications
    #     for event_notification_data in event_notifications_data:
    #         notification = EventNotification.objects.create(event=instance, **event_notification_data)

    #     return instance

    def to_representation(self, instance):
        self.fields["organiser"] = UserSerializer()
        return super(EventSerializer, self).to_representation(instance)
