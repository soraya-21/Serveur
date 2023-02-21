from django.urls import path
from .views import spotify_webhookAPIView

urlpatterns = [
    path('', spotify_webhookAPIView.as_view(), name='spotify-webhook'),
]
