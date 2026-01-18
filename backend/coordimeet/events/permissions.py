from rest_framework import permissions
from rest_framework.request import Request

from coordimeet.events.models import Event, EventTypeChoices
from coordimeet.users.models import CoordimeetGroup, CoordimeetUser, CoordimeetMemberRole
from coordimeet.users.services import CoordimeetUserServices


def _has_group_permission(coordimeet_user: CoordimeetUser, coordimeet_group: CoordimeetGroup, roles: list[CoordimeetMemberRole]):
    member = coordimeet_group.coordimeet_members.filter(coordimeet_user=coordimeet_user).first()
    if member:
        return member.role in roles
    return False


class HasGroupOwnerOrAdminPermission(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: CoordimeetGroup):
        coordimeet_user = CoordimeetUserServices.get_or_create_coordimeet_user_from_request(request)
        return _has_group_permission(coordimeet_user, obj, [CoordimeetMemberRole.ADMIN, CoordimeetMemberRole.OWNER])


class HasGroupOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: CoordimeetGroup):
        coordimeet_user = CoordimeetUserServices.get_or_create_coordimeet_user_from_request(request)
        return _has_group_permission(coordimeet_user, obj, [CoordimeetMemberRole.OWNER])


class IsEventOrganiserOrAdminInOrganiserGroup(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: Event):
        coordimeet_user = CoordimeetUserServices.get_or_create_coordimeet_user_from_request(request)
        if obj.organiser == coordimeet_user:
            return True
        if obj.is_group_organiser and obj.invited_group:
            return _has_group_permission(coordimeet_user, obj.invited_group, [CoordimeetMemberRole.ADMIN, CoordimeetMemberRole.OWNER])
        return False


class IsEventOrganiserOrOwnerInOrganiserGroup(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: Event):
        coordimeet_user = CoordimeetUserServices.get_or_create_coordimeet_user_from_request(request)
        if obj.organiser == coordimeet_user:
            return True
        if obj.is_group_organiser and obj.invited_group:
            return _has_group_permission(coordimeet_user, obj.invited_group, [CoordimeetMemberRole.OWNER])
        return False


class IsPublicEventOrUserIsMember(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: Event):
        coordimeet_user = CoordimeetUserServices.get_or_create_coordimeet_user_from_request(request)
        return (
            obj.event_type == EventTypeChoices.PUBLIC or
            (
                request.user.is_authenticated
                and obj.event_type in [EventTypeChoices.GROUP, EventTypeChoices.CLOSED]
                and obj.invited_group.coordimeet_members.filter(coordimeet_user=coordimeet_user).exists()
            )
        )
