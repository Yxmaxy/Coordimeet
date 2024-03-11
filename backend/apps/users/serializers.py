from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainSlidingSerializer


from django.contrib.auth import get_user_model


class CustomTokenObtainSlidingSerializer(TokenObtainSlidingSerializer):
     """
     Custom token serializer to include the `user_id` in the response.
     """
     def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        data["id"] = user.id

        return data


class UserSerializer(ModelSerializer):
    """
    Serializer for the user object.
    """

    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "email"]
