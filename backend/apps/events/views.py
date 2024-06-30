from icalendar import Calendar, Event as ICalEvent

from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from apps.utils.permissions import IsEventOrganiserOrAdminInOrganiserGroup, IsPublicEventOrUserIsMember
from apps.users.models import MemberRole
from apps.events.models import Event, EventParticipant, EventParticipantAvailability, EventTypeChoices
from apps.events.serializers import EventSerializer, EventParticipantSelectedSerializer, EventFinishSerializer
from apps.events.services import EventServices


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

        all_events = Event.objects.filter(
            Q(event_type=EventTypeChoices.PUBLIC)
            & Q(event_participants__user=self.request.user)
            | Q(event_type__in=[EventTypeChoices.GROUP, EventTypeChoices.CLOSED])
            & Q(invited_group__members__user=self.request.user)
        ).distinct().order_by("-created_at")
        exclude_events = Event.objects.filter(
            Q(organiser=self.request.user)
            | Q(is_group_organiser=True)
            & Q(invited_group__members__user=self.request.user)
            & Q(invited_group__members__role__in=[MemberRole.OWNER, MemberRole.ADMIN])
        ).distinct().order_by("-created_at")

        return all_events.exclude(event_uuid__in=exclude_events.values_list("event_uuid", flat=True))


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
    permission_classes = [IsPublicEventOrUserIsMember]

    def get(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        self.check_object_permissions(request, event)

        if not event.selected_start_date and event.deadline < timezone.now():
            best_date_ranges = EventServices.get_best_date_range(event)
            if not best_date_ranges:  # should not happen
                return

            best_range = best_date_ranges[0]
            event.selected_start_date = best_range["range"]["start_date"]
            event.selected_end_date = best_range["range"]["end_date"]
            event.save()

        if event.event_type in [EventTypeChoices.GROUP, EventTypeChoices.CLOSED]:
            if not IsAuthenticated().has_permission(request, self):
                return Response({"message": "Not allowed"}, status=403)

        serializer = EventSerializer(event, partial=True, context={"request": request})
        return Response(serializer.data)
    
    def put(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        self.check_object_permissions(request, event)

        if (
            not IsAuthenticated().has_permission(request, self)
            or not IsEventOrganiserOrAdminInOrganiserGroup().has_object_permission(request, self, event)
        ):
            return Response({"message": "Not allowed"}, status=403)

        serializer = EventSerializer(event, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EventParticipantAPIView(APIView):
    permission_classes = [IsAuthenticated, IsPublicEventOrUserIsMember]

    def get(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        self.check_object_permissions(request, event)
        try:
            participant = EventParticipant.objects.get(event=event, user=request.user)
        except EventParticipant.DoesNotExist:
            participant = None
        serializer = EventParticipantSelectedSerializer(participant)
        return Response(serializer.data)
    
    def post(self, request, event_uuid):
        event = Event.objects.get(event_uuid=event_uuid)
        self.check_object_permissions(request, event)

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
    permission_classes = [IsAuthenticated, IsEventOrganiserOrAdminInOrganiserGroup]

    def get(self, request, event_uuid):
        """Get participants for the event"""
        event = Event.objects.get(event_uuid=event_uuid)
        self.check_object_permissions(request, event)

        participants = EventParticipant.objects.filter(event=event)
        serializer = EventParticipantSelectedSerializer(participants, many=True)
        return Response(serializer.data)

    def post(self, request, event_uuid):
        """Select the selected_start_date and selected_end_date for the event"""
        event = Event.objects.get(event_uuid=event_uuid)
        self.check_object_permissions(request, event)

        serializer = EventFinishSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Selected dates saved"})


class EventICalendarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_uuid=None):
        """
        Read the iCalendar file provided from the request and return the date ranges of times when the user is unavailable
        """
        ical_file = request.FILES["file"]
        cal = Calendar.from_ical(ical_file.read())
        unavailable_times = []
        for component in cal.walk():
            if component.name == "VEVENT":
                start = component.get("dtstart").dt
                end = component.get("dtend").dt
                unavailable_times.append({"event_start": start, "event_end": end})
        return Response(unavailable_times)

    def get(self, request, event_uuid):
        """
        Return the iCalendar file with the event's selected date ranges, name and description
        """
        event = Event.objects.get(event_uuid=event_uuid)
        if event.selected_start_date is None or event.selected_end_date is None:
            return Response({"message": "Event is not finished yet."}, status=400)

        cal = Calendar()
        ical_event = ICalEvent()
        ical_event.add("summary", event.title)
        ical_event.add("dtstart", event.selected_start_date)
        ical_event.add("dtend", event.selected_end_date)
        ical_event.add("description", event.description)
        cal.add_component(ical_event)

        response = HttpResponse(cal.to_ical(), content_type="text/calendar")
        response["Content-Disposition"] = "attachment; filename=event.ics"
        return response
