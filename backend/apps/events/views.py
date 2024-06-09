from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q

from apps.events.models import Event, EventParticipant
from apps.events.serializers import EventSerializer, EventParticipantSelectedSerializer


class EventListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get_queryset(self):
        # TODO: extend with events I'm invited to
        return Event.objects.filter(organiser=self.request.user).order_by("-created_at")


class EventManageAPIView(APIView):
    def get(self, request, event_uuid):
        # TODO: permissions based on event settings

        event = Event.objects.get(event_uuid=event_uuid)
        serializer = EventSerializer(event)
        return Response(serializer.data)
    
    def put(self, request, event_uuid):
        pass


class EventParticipantListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]  # TODO: permission if event has public participants
    serializer_class = EventParticipantSelectedSerializer

    def get_queryset(self, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        return EventParticipant.objects.filter(event=event)


class EventParticipantAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        participants = EventParticipant.objects.filter(event=event, user=request.user, not_comming=False)

        return Response(
            {
                "selected_ranges": [
                    {
                        "start_date": participant.start_date,
                        "end_date": participant.end_date,
                    }
                    for participant in participants
                ],
            }
        )
    
    def post(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        # TODO: check if user is invited

        # remove existing participations
        EventParticipant.objects.filter(event=event, user=request.user).delete()

        if "not_comming" in request.data:
            EventParticipant.objects.create(
                event=event,
                user=request.user,
                not_comming=True,
            )
        else:  # create participant ranges
            for selected_range in request.data["selected_ranges"]:
                EventParticipant.objects.create(
                    event=event,
                    user=request.user,
                    start_date=selected_range["start_date"],
                    end_date=selected_range["end_date"],
                )

        return Response({"message": "Participation saved"})


class EventOrganiserAPIView(APIView):
    permission_classes = [IsAuthenticated]  # TODO: add if user is event organiser

    def get(self, request, event_uuid):
        """Get participants for the event"""
        event = Event.objects.get(event_uuid=event_uuid)
        participants = EventParticipant.objects.filter(event=event)
        serializer = EventParticipantSelectedSerializer(participants, many=True)
        return Response(serializer.data)

    def post(self, request, event_uuid):
        """Select the selected_start_date and selected_end_date for the event"""
        event = Event.objects.get(event_uuid=event_uuid)

        event.selected_start_date = request.data["selected_start_date"]
        event.selected_end_date = request.data["selected_end_date"]
        event.save()

        return Response({"message": "Selected dates saved"})
