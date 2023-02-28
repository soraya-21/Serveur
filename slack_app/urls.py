from django.urls import path
from .views import slack_webhookAPIView

urlpatterns = [
    path('', slack_webhookAPIView.as_view(), name='slack-webhook')
]
