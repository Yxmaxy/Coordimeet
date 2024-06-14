from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q

from apps.utils.permissions import IsEventOrganiserOrAdminInOrganiserGroup, IsEventOrganiserOrOwnerInOrganiserGroup
from apps.users.models import MemberRole
from apps.events.models import Event, EventParticipant, EventParticipantAvailability, EventTypeChoices
from apps.events.serializers import EventSerializer, EventParticipantSelectedSerializer


class EventInvitedListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get_queryset(self):
        # get the following events:
        # - if the event_type is PUBLIC - if the user submitted a participation (they exist in EventParticipant)
        # - if the event_type is GROUP or CLOSED - if the user is a member of the invited_group
        # exlcude the following events:
        # - if the user is the organiser
        # - if the user is a member of the invited_group and is_group_organiser is True and the user's role is OWNER or ADMIN

        return Event.objects.filter(
            Q(event_type=EventTypeChoices.PUBLIC) & Q(event_participants__user=self.request.user)
            | Q(event_type__in=[EventTypeChoices.GROUP, EventTypeChoices.CLOSED])
            & Q(invited_group__members__user=self.request.user)
        ).exclude(
            Q(organiser=self.request.user)
            | Q(is_group_organiser=True)
            & Q(invited_group__members__user=self.request.user)
            & Q(invited_group__members__role__in=[MemberRole.OWNER, MemberRole.ADMIN])
        ).distinct().order_by("-created_at")


class EventOrganiserListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsEventOrganiserOrAdminInOrganiserGroup]
    serializer_class = EventSerializer

    def get_queryset(self):
        # get the following events:
        # - if the user is the organiser
        # - if the user is a member of the invited_group and is_group_organiser is True and the user's role is OWNER or ADMIN
        return Event.objects.filter(
            Q(organiser=self.request.user)
            | Q(is_group_organiser=True)
            & Q(invited_group__members__user=self.request.user)
            & Q(invited_group__members__role__in=[MemberRole.OWNER, MemberRole.ADMIN])
        ).distinct().order_by("-created_at")


class EventManageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEventOrganiserOrAdminInOrganiserGroup]

    def get(self, request, event_uuid):
        # TODO: permissions based on event settings

        event = Event.objects.get(event_uuid=event_uuid)
        serializer = EventSerializer(event, partial=True, context={"request": request})
        return Response(serializer.data)
    
    def put(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        serializer = EventSerializer(event, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EventParticipantListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventParticipantSelectedSerializer

    def get_queryset(self, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        return EventParticipant.objects.filter(event=event)


class EventParticipantAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        try:
            participant = EventParticipant.objects.get(event=event, user=request.user)
        except EventParticipant.DoesNotExist:
            participant = None
        serializer = EventParticipantSelectedSerializer(participant)
        return Response(serializer.data)
    
    def post(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        # TODO: check if user is invited

        event_participant, _ = EventParticipant.objects.get_or_create(
            event=event,
            user=request.user,
        )

        # remove existing participation availabilities
        EventParticipantAvailability.objects.filter(participant=event_participant).delete()

        if "not_comming" in request.data:
            event_participant.not_comming = True
        else:  # create participant ranges
            event_participant.not_comming = False
            for availability in request.data["participant_availabilities"]:
                EventParticipantAvailability.objects.create(
                    participant=event_participant,
                    start_date=availability["start_date"],
                    end_date=availability["end_date"],
                )
        event_participant.save()
        return Response({"message": "Participation saved"})


class EventOrganiserAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEventOrganiserOrOwnerInOrganiserGroup]

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
