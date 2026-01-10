from functools import wraps

from coordimeet.users.services import CoordimeetUserServices


def with_coordimeet_user(view_func):
    """
    Decorator that adds a coordimeet_user attribute to the request object.
    The coordimeet_user is retrieved using CoordimeetUserServices.get_or_create_coordimeet_user_from_request.
    """
    @wraps(view_func)
    def wrapper(self, *args, **kwargs):
        self.coordimeet_user = CoordimeetUserServices.get_or_create_coordimeet_user_from_request(self)
        return view_func(self, *args, **kwargs)
    return wrapper
