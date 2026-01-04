from coordimeet.users.models import CoordimeetUser

from django.contrib.auth.models import AbstractUser


class CoordimeetUserServices:
    @staticmethod
    def get_coordimeet_user(user: AbstractUser) -> CoordimeetUser:
        coordimeet_user, _ = CoordimeetUser.objects.get_or_create(user=user)
        return coordimeet_user
