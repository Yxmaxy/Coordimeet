from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated


from apps.events.models import Event
from apps.events.serializers import EventSerializer


class EventListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get_queryset(self):
        # TODO: extend with events I'm invited to
        return Event.objects.filter(organiser=self.request.user)

class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    # TODO: might have to have one api view for getting the event and another for logged in users to update/delete
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    lookup_field = "event_uuid"
