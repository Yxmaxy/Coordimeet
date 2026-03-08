from django.contrib import admin

from coordimeet.users.models import CoordimeetUser
from coordimeet.friends.models import CoordimeetFriend

admin.site.register(CoordimeetUser)
admin.site.register(CoordimeetFriend)
