from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.events.models import Event
from apps.events.serializers import EventSerializer


class EventListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get_queryset(self):
        # TODO: extend with events I'm invited to
        return Event.objects.filter(organiser=self.request.user)

class EventManageAPIView(APIView):
    def get(self, request, event_uuid):
        # TODO: permissions based on event settings

        event = Event.objects.get(event_uuid=event_uuid)

        # TODO: "Organiser" serializer with more data

        serializer = EventSerializer(event)
        return Response(serializer.data)
    
    def put(self, request, event_uuid):
        pass
