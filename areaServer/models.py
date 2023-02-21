from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self,username,email,password=None):
        if not username:
            raise TypeError('Users should have a username')
        if not email:
            raise TypeError('Users should have an email')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,username,email,password=None):
        if not password:
            raise TypeError("Password shouldn't be none")

        user = self.create_user(username,email,password)
        user.is_superuser = True
        user.is_staff=True
        user.save()
        return user

AUTH_PROVIDERS = {'google':'google', 'email':'email'}

class User(AbstractBaseUser,PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255,db_index=True, null=True)
    email = models.EmailField(unique=True,db_index=True, null=True)
    is_verified=models.BooleanField(default=False, null=True)
    is_active= models.BooleanField(default=True, null=True)
    is_staff= models.BooleanField(default=False, null=True)
    created_at=models.DateTimeField(auto_now_add=True, null=True)
    updated_at=models.DateTimeField(auto_now=True, null=True)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    spotify_tokens = models.JSONField(default=dict, null=True)
    linkedin_token = models.CharField(max_length=255, blank=False, null=True)    
    reddit_tokens = models.JSONField(default=dict, null=True)
    gitlab_tokens = models.JSONField(default=dict, null=True)

 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects=UserManager()

    def __str__(self):
        return self.email 
    
    def tokens(self):
        refresh =  RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
