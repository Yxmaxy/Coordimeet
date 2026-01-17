from django.db import models

from coordimeet.users.models import CoordimeetUser


class CoordimeetFriend(models.Model):
    user = models.ForeignKey(CoordimeetUser, on_delete=models.CASCADE, related_name="friend_from")
    friend = models.ForeignKey(CoordimeetUser, on_delete=models.CASCADE, related_name="friend_to")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.friend}"
