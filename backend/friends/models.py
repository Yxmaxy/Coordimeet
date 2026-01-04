from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_from")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend_to")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.friend}"


admin.site.register(Friend)
