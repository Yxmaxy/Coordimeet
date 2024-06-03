from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.events.models import Event, EventParticipant
from apps.events.serializers import EventSerializer


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

        # TODO: "Organiser" serializer with more data

        serializer = EventSerializer(event)
        return Response(serializer.data)
    
    def put(self, request, event_uuid):
        pass


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


class EventFinishAPIView(APIView):
    def post(self, request, event_uuid):
        # TODO
        # event = Event.objects.get(event_uuid=event_uuid)
        # event.save()
        return Response({"message": "Event finished"})