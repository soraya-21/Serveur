from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import generics, status, views, permissions
from .serializers import RegisterSerializer, EmailVerificationSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from.utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

# Create your views here.

class RegisterView(generics.GenericAPIView):
    serializer_class=RegisterSerializer

    def post(self,request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        email = user['email']
        check_user_exist = User.objects.filter(email=email).exists()
        if check_user_exist:
            return Response({'error': 'User already registered'}, status.HTTP_400_BAD_REQUEST)

        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        token = Util.generate_jwt(user.email)
        current_site=get_current_site(request).domain
        relativeLink=reverse('email-verify')
        absurl='http://'+ current_site + relativeLink + "?token="+str(token)
        email_body= 'Hi ' + user.username + ' Use link below to verify your email \n'+ absurl
        data={'email_body':email_body, 'to_email': user.email, 'email_subject': "Verify your email"}
        Util.send_email(data)
        return Response(user_data,status.HTTP_201_CREATED)

class VerifyEmail(views.APIView):
    serializer_class=EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY,type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        try:
            token = request.GET.get('token')
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            print(payload['email'])
            user = User.objects.get(email=payload['email'])
            if user.is_verified:
                return Response({'error': 'User is already verified'}, status.HTTP_400_BAD_REQUEST)
            user.is_verified = True
            user.save()
            return Response({'email': f"{user.username} account successfully activated"}, status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': "Activation link expired"}, status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': "Invalid token"}, status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': "Invalid user_id in token"}, status.HTTP_400_BAD_REQUEST)

class LoginAPIView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status.HTTP_200_OK)

# class LogoutAPIView(generics.GenericAPIView):
#     serializer_class = LogoutSerializer
#     permission_classes = (permissions.IsAuthenticated)

#     def post(self, request):
#         serializer= self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(status=status.HTTP_204_NO_CONTENT)
