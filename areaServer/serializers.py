from rest_framework import serializers
from .models import User
from django.core.validators import validate_email
from validate_email import validate_email
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
is_valid = validate_email('example@example.com', verify=True)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68,min_length=6,write_only=True)
    class Meta:
        model = User
        fields=("username", "email", "password")
    
    def validate(self,attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not validate_email(email):
            raise serializers.ValidationError('Enter valid Email')
            
        if not username.isalnum():
            raise serializers.ValidationError("The username should only contain alphanumeric characters")
        
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class EmailVerificationSerializer (serializers.ModelSerializer):
    token = serializers.CharField(max_length = 255)

    class Meta:
        model=User
        fields=['token']

class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255,  min_length=3)
    password=serializers.CharField(max_length=68, min_length=6, write_only=True)
    username=serializers.CharField(max_length=68, min_length=3,read_only=True)
    # tokens=serializers.CharField(max_length=68, min_length=6,read_only=True)

    class Meta:
        model=User
        fields=['email', 'password', 'username']
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Your account has been disabled, contact your admin')
        if not user.is_active:
            raise AuthenticationFailed('Email is not verified')

        return {
            "email":user.email,
            "username":user.username,
            # "tokens":user.tokens
        }

# class LogoutSerializer(serializers.Serializer):
#     refresh = serializers.CharField()

#     def validate(self, attrs):
#         self.token = attrs['refresh']

#         return attrs

#     def save(self, **kwargs):
#         try:
#             RefreshToken(self.token).blacklist()
#         except TokenError:
#             self.fail('bad token')