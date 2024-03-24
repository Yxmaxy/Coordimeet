from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.events.models import Event, EventAvailabilityOption
from apps.users.serializers import UserSerializer


class EventAvailabilityOptionSerializer(serializers.ModelSerializer):
    """Serializer for the EventAvailabilityOption model"""

    class Meta:
        model = EventAvailabilityOption
        fields = ["start_date", "end_date"]


class EventSerializer(serializers.ModelSerializer):
    """Serializer for the Event model"""

    event_availability_options = EventAvailabilityOptionSerializer(many=True)
    organiser = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    class Meta:
        model = Event
        fields = "__all__"
    
    def create(self, validated_data):
        availability_options_data = validated_data.pop("event_availability_options")
        event = Event.objects.create(**validated_data)
        for availability_option_data in availability_options_data:
            EventAvailabilityOption.objects.create(event=event, **availability_option_data)
        return event

    def to_representation(self, instance):
        self.fields["organiser"] = UserSerializer()
        return super(EventSerializer, self).to_representation(instance)
