from django.shortcuts import render
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseBadRequest
from rest_framework import generics, status
from areaServer.utils import Util
from rest_framework.response import Response
import os
from .serializers import RedditSerializer
import json
from areaServer.models import User
import requests

# Create your views here.
# get user information via access token, check if user in db, stock token and refresh token, refresh avant chaque area  
# oauth_token = ''
artist_name = "Passenger"

class reddit_webhookAPIView(generics.GenericAPIView):
    serializer_class = RedditSerializer

    client_id = os.environ.get('AREA_REDDIT_ID')
    client_secret = os.environ.get('AREA_REDDIT_SECRET')

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
            # print(f"email ====> {reponse_data['email']}")
            token_endpoint = "https://www.reddit.com/api/v1/access_token"
            auth_header = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
            auth_data = {
                "grant_type": "authorization_code",
                "code": reponse_data["code"],
                "redirect_uri": 'http://127.0.0.1:8000/reddit/'
            }
            headers = {
                "User-Agent": "python:area_red:1.0 (by /u/Soraya_Anais)",
            }
            response = requests.post(token_endpoint, auth=auth_header, data=auth_data, headers=headers)

            if response.status_code == 200:
                print(response.json())
                access_token = response.json()["access_token"]
                print(f"access_token ====> {access_token}")
            else:
                print("Error:", response.text)
            headers["Authorization"] = f"Bearer {access_token}"
            params = {
                "scope": "identity"
            }
            
    def get(self, request):
        """Pour les requetes GET"""
        self.get_token(request)
        # self.follow_artist(self.user_email, artist_name)
        return Response({'msg', 'getting auth code'})

    def post(self, request):
        """Pour les requetes POST"""
        # self.follow_artist(self.user_email, artist_name)
        return Response({'msg', 'getting auth code'})