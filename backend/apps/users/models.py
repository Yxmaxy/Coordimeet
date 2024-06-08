import uuid

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.users.managers import CoordimeetUserManager


class UserTypes(models.IntegerChoices):
    """
    Enum to represent the type of user
    """

    DEFAULT = 1, "Default"
    ANONYMOUS = 2, "Anonymous"


class CoordimeetUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for Coordimeet
    """

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField("Date joined", default=timezone.now)
    user_type = models.IntegerField(choices=UserTypes.choices, default=UserTypes.DEFAULT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CoordimeetUserManager()

    def __repr__(self):
        return self.email
    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        return self.email


class CoordimeetGroup(models.Model):
    """
    Model to represent a group of users
    """

    name = models.CharField(max_length=150)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    is_closed = models.BooleanField(default=False)  # group is automatically created and can't be edited

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name


@receiver(post_save, sender=CoordimeetGroup)
def post_save_group(sender, instance: CoordimeetGroup, created, **kwargs):
    """Creates group post save if it doesn't exist yet"""
    if created:
        instance.group = Group.objects.create(name=instance.uuid)
        instance.save()


@receiver(post_delete, sender=CoordimeetGroup)
def post_delete_group(sender, instance: CoordimeetGroup, **kwargs):
    """Deletes group post delete"""
    instance.group.delete()


class MemberRole(models.IntegerChoices):
    """
    Enum to represent the role of a member in a group
    """

    ADMIN = 1, "Admin"
    MEMBER = 2, "Member"
    OWNER = 3, "Owner"


class Member(models.Model):
    """
    Model to represent a member of a group
    """

    user = models.ForeignKey(CoordimeetUser, on_delete=models.CASCADE)
    group = models.ForeignKey(CoordimeetGroup, on_delete=models.CASCADE, related_name="members")
    role = models.IntegerField(choices=MemberRole.choices, default=MemberRole.MEMBER)

    @property
    def is_admin(self):
        return self.role == MemberRole.ADMIN
    
    def __repr__(self):
        return f"{self.user} - {self.group}"
    
    def __str__(self):
        return f"{self.user} in {self.group}"
