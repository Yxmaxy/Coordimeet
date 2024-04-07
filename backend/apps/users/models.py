from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from apps.users.managers import CoordimeetUserManager


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

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name


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
