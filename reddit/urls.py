from django.urls import path
from .views import reddit_webhookAPIView

urlpatterns = [
    path('', reddit_webhookAPIView.as_view(), name='reddit-webhook'),
]
