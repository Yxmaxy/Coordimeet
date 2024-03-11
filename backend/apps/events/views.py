from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated


from apps.events.models import Event
from apps.events.serializers import EventSerializer


class EventListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.filter(organiser=self.request.user)
