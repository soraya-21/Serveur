from django.urls import path
from .views import slack_news_webhookAPIView, slack_click_up_webhookAPIView

urlpatterns = [
    path('news', slack_news_webhookAPIView.as_view(), name='slack-news-webhook'),
    path('send_created_task', slack_click_up_webhookAPIView.as_view(), name='slack-click-up-webhook')
]
