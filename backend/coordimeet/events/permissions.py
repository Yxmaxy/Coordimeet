from rest_framework import permissions
from rest_framework.request import Request

from coordimeet.events.models import Event, EventTypeChoices
from coordimeet.users.models import CoordimeetGroup, CoordimeetMemberRole


def _has_group_permission(request: Request, group: CoordimeetGroup, roles: list[CoordimeetMemberRole]):
    current_user = request.user
    member = group.members.filter(user=current_user).first()
    if member:
        return member.role in roles
    return False


class HasGroupOwnerOrAdminPermission(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: CoordimeetGroup):
        return _has_group_permission(request, obj, [CoordimeetMemberRole.ADMIN, CoordimeetMemberRole.OWNER])


class HasGroupOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: CoordimeetGroup):
        return _has_group_permission(request, obj, [CoordimeetMemberRole.OWNER])


class IsEventOrganiserOrAdminInOrganiserGroup(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: Event):
        if obj.organiser == request.user:
            return True
        if obj.is_group_organiser and obj.invited_group:
            return _has_group_permission(request, obj.invited_group, [CoordimeetMemberRole.ADMIN, CoordimeetMemberRole.OWNER])
        return False


class IsEventOrganiserOrOwnerInOrganiserGroup(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: Event):
        if obj.organiser == request.user:
            return True
        if obj.is_group_organiser and obj.invited_group:
            return _has_group_permission(request, obj.invited_group, [CoordimeetMemberRole.OWNER])
        return False


class IsPublicEventOrUserIsMember(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: Event):
        return (
            obj.event_type == EventTypeChoices.PUBLIC or
            (
                request.user.is_authenticated
                and obj.event_type in [EventTypeChoices.GROUP, EventTypeChoices.CLOSED]
                and obj.invited_group.members.filter(user=request.user).exists()
            )
        )
