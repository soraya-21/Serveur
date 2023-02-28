from django.shortcuts import render
from .serializers import slackSerializer
from django.shortcuts import render
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseBadRequest
from rest_framework import generics, status
from areaServer.utils import Util
from rest_framework.response import Response
import os
from areaServer.models import User
import requests

# Create your views here.

class slack_webhookAPIView(generics.GenericAPIView):
    serializer_class = slackSerializer
    
    def get_token(self, request):
        if request.method == "GET":
            try:
                reponse_data = {
                    "code": request.GET.get('code'),
                    "email" : request.GET.get('email')
                }
            except:
                return HttpResponse("No code found", status=400)
            print(f"code ====> {reponse_data['code']}")

    def get(self, request):
        """Pour les requetes GET"""
        self.get_token(request)
        # self.follow_artist(self.user_email, artist_name)
        return Response({'msg', 'getting auth code'})