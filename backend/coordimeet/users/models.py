import uuid

from django.db import models
from django.conf import settings


class CoordimeetPermissions(models.Model):
    class Meta:
        permissions = [
            ("coordimeet_app_enabled", "Is the coordimeet app enabled for the user"),
        ]


class CoordimeetUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coordimeet_user",
        blank=True,
        null=True,
    )
    anonymous_username = models.CharField(
        unique=True,
        max_length=150,
        blank=True,
        null=True,
    )

    @property
    def username(self) -> str:
        if not self.is_anonymous:
            return self.user.get_username()
        return self.anonymous_username

    @property
    def is_anonymous(self) -> bool:
        return self.user is None

    def __str__(self) -> str:
        return self.username


class CoordimeetGroup(models.Model):
    name = models.CharField(max_length=150)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_closed = models.BooleanField(
        default=False,
        help_text="Group is automatically created and can't be edited"
    )

    def __str__(self):
        return self.name


class CoordimeetMemberRole(models.IntegerChoices):
    ADMIN = 1, "Admin"
    MEMBER = 2, "Member"
    OWNER = 3, "Owner"


class CoordimeetMember(models.Model):
    user = models.ForeignKey(
        CoordimeetUser,
        on_delete=models.CASCADE,
        related_name="member"
    )
    group = models.ForeignKey(
        CoordimeetGroup,
        on_delete=models.CASCADE,
        related_name="members"
    )
    role = models.IntegerField(
        choices=CoordimeetMemberRole.choices,
        default=CoordimeetMemberRole.MEMBER
    )

    def __str__(self):
        return f"{self.user} in {self.group}"
