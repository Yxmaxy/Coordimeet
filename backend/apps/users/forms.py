from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from apps.users.models import CoordimeetUser


class CoordimeetUserCreationForm(UserCreationForm):

    class Meta:
        model = CoordimeetUser
        fields = ("email",)


class CoordimeetUserChangeForm(UserChangeForm):

    class Meta:
        model = CoordimeetUser
        fields = ("email",)
