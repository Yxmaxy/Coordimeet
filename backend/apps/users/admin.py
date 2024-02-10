from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.forms import CoordimeetUserCreationForm, CoordimeetUserChangeForm
from apps.users.models import CoordimeetUser


class CoordimeetUserAdmin(UserAdmin):
    add_form = CoordimeetUserCreationForm
    form = CoordimeetUserChangeForm
    model = CoordimeetUser

    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(CoordimeetUser, CoordimeetUserAdmin)
