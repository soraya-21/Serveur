from django.urls import path
from .views import spotify_following_webhookAPIView

urlpatterns = [
    path('', spotify_following_webhookAPIView.as_view(), name='spotify-webhook'),
]
