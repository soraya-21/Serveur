from django.urls import path
from .views import Youtube_webhookAPIView
from .views import login, oauth2callback, like_video, get_subsriptions

urlpatterns = [
   # path('', Youtube_webhookAPIView.as_view(), name='youtube-webhook'),
    path('', Youtube_webhookAPIView.as_view(), name='youtube-webhook'),
    path('login/', login, name='login'),
    path('like-video/', like_video, name='like_video'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
    path('get_subsriptions/', get_subsriptions, name='get_subsriptions'),
   # path('my_view/', my_view, name='my_view'),
]