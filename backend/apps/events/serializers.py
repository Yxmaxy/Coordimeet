from rest_framework import serializers

from apps.events.models import Event, EventAvailabilityOption


# class EventAvailabilityOptionSerializer(serializers.ModelSerializer):
#     """Serializer for the EventAvailabilityOption model"""

#     event = serializers.PrimaryKeyRelatedField(
#         queryset=Event.objects.all(), required=False
#     )

#     class Meta:
#         model = EventAvailabilityOption
#         fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    """Serializer for the Event model"""

    event_availability_options = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field="event",
        queryset=EventAvailabilityOption.objects.all(),
    )

    class Meta:
        model = Event
        fields = "__all__"
