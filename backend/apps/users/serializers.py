from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from django.contrib.auth import get_user_model


class CustomTokenObtainSlidingSerializer(TokenObtainPairSerializer):
     """
     Custom token serializer to include the `user_id` in the response.
     """
     def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        data["id"] = user.id

        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object.
    TODO: extend with other fields like the image, etc.
    """
    
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email"]
