from rest_framework import serializers
from .models import User

class YoutubeSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = User
        fields=("username", "email", "password")