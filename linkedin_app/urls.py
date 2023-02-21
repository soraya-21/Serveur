from django.urls import path
from .views import Linkedin_webhookAPIView

urlpatterns = [
    path('', Linkedin_webhookAPIView.as_view(), name='reddit-webhook'),
]
