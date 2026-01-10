from typing import Optional
from uuid import uuid4
from wonderwords import RandomWord

from rest_framework.request import Request
from rest_framework.response import Response

from django.contrib.auth.models import AbstractUser

from coordimeet.users.models import CoordimeetUser

ANONYMOUS_USER_COOKIE_NAME = "coordimeet_anonymous_username"
ANONYMOUS_USER_COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 1 year


class CoordimeetUserServices:
    @staticmethod
    def get_coordimeet_user_from_request(request: Request) -> Optional[CoordimeetUser]:
        if request.user.is_authenticated:
            return CoordimeetUserServices.get_or_create_authenticated_coordimeet_user(request.user)

        if anonymous_user := CoordimeetUserServices.get_anonymous_user_from_cookie(request):
            return anonymous_user

        return None

    @staticmethod
    def get_or_create_coordimeet_user_from_request(request: Request) -> CoordimeetUser:
        if coordimeet_user := CoordimeetUserServices.get_coordimeet_user_from_request(request):
            return coordimeet_user
        return CoordimeetUserServices.create_anonymous_user()

    @staticmethod
    def get_or_create_authenticated_coordimeet_user(user: AbstractUser) -> CoordimeetUser:
        coordimeet_user, _ = CoordimeetUser.objects.get_or_create(user=user)
        return coordimeet_user

    @staticmethod
    def get_anonymous_user_from_cookie(request: Request) -> Optional[CoordimeetUser]:
        if coordimeet_anonymous_username := request.COOKIES.get(ANONYMOUS_USER_COOKIE_NAME):
            try:
                return CoordimeetUser.objects.get(anonymous_username=coordimeet_anonymous_username)
            except CoordimeetUser.DoesNotExist:
                return None
        return None

    @staticmethod
    def create_anonymous_user() -> CoordimeetUser:
        random_word = RandomWord()
        username_sections = [
            random_word.word(include_parts_of_speech=["adjectives"]),
            random_word.word(include_parts_of_speech=["nouns"]),
            uuid4().hex[:10],
        ]

        anonymous_username = "-".join(username_sections)
        coordimeet_user = CoordimeetUser.objects.create(anonymous_username=anonymous_username)
        return coordimeet_user

    @staticmethod
    def set_anonymous_user_cookie(response: Response, anonymous_username: str) -> None:
        """Set cookie for anonymous user to persist across browser sessions."""
        response.set_cookie(
            ANONYMOUS_USER_COOKIE_NAME,
            anonymous_username,
            max_age=ANONYMOUS_USER_COOKIE_MAX_AGE,
            httponly=True,
            samesite="Lax",
        )

