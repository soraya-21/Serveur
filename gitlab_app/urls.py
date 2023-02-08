from django.urls import path
from .views import Gitlab_webhookAPIView

urlpatterns = [
    path('', Gitlab_webhookAPIView.as_view(), name='gitlab-webhook'),
]
