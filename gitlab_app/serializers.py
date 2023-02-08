from rest_framework import serializers
from .models import User
from django.core.validators import validate_email
from validate_email import validate_email
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed

class GitlabSerializer(serializers.ModelSerializer):
    username = serializers.CharField()