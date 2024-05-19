from rest_framework import permissions
from rest_framework.request import Request

from apps.users.models import CoordimeetGroup, MemberRole


def _has_group_permission(request: Request, group: CoordimeetGroup, roles: list[MemberRole]):
    current_user = request.user
    member = group.members.filter(user=current_user).first()
    if member:
        return member.role in roles
    return False


class HasGroupOwnerOrAdminPermission(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: CoordimeetGroup):
        return _has_group_permission(request, obj, [MemberRole.ADMIN, MemberRole.OWNER])


class HasGroupOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request: Request, view, obj: CoordimeetGroup):
        return _has_group_permission(request, obj, [MemberRole.ADMIN, MemberRole.OWNER])
