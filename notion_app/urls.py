from django.urls import path
from .views import notion_webhookAPIView

urlpatterns = [
    path('', notion_webhookAPIView.as_view(), name='notion-webhook')
]
