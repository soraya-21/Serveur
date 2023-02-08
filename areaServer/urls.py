from django.urls import re_path as url
from django.urls import path
from areaServer import views
from .views import RegisterView,VerifyEmail, LoginAPIView

urlpatterns=[
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    # path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
]