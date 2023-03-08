from django.shortcuts import render
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseBadRequest
from rest_framework import generics, status
from areaServer.utils import Util
from rest_framework.response import Response
import os
from .serializers import Spotify_following_Serializer
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
import json
from areaServer.models import User

# Create your views here.
# get user information via access token, check if user in db, stock token and refresh token, refresh avant chaque area  
# oauth_token = ''
# artist_name = "Passenger"

user_email  = None
class spotify_following_webhookAPIView(generics.GenericAPIView):
    serializer_class = Spotify_following_Serializer

    # user_email = "soraya.codo@epitech.eu"
    client_id = os.environ.get('AREA_SPOTIFY_ID')
    client_secret = os.environ.get('AREA_SPOTIFY_SECRET')
    redirect_uri = 'http://127.0.0.1:8000/spotifyyy_app_following/'
    scope = "user-follow-modify", "user-read-email", "user-read-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
    auth_url = sp.auth_manager.get_authorize_url()
    print(auth_url)

    def get_authorization_code(self, request):
        try:
            reponse_data = {
                "code": request.GET.get('code')
            }
        except:
            return HttpResponse("No code found", status=400)
        # print (reponse_data["code"])
        response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": reponse_data["code"],
            "redirect_uri": self.redirect_uri,
        },
        auth=(self.client_id, self.client_secret),
        )
        # print (response.json())
        oauth_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]

        url = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization": "Bearer {}".format(oauth_token)
        }
        response = requests.get(url, headers=headers)
        print(response.json())
        global user_email
        user_email = response.json()["email"]
        
        user = User.objects.filter(email=user_email).first()
        if not user:
            return ("User not in db")
        else:
            user.spotify_tokens = {
                "spotify_access_token" : oauth_token,
                "spotify_refresh_token" : refresh_token
            }
            user.save()
                
        return oauth_token, refresh_token, user_email
    
    def get_token_in_db(self, user_email):
        user = User.objects.filter(email=user_email).first()
        oauth_token = user.spotify_tokens["spotify_access_token"]
        return oauth_token

    def get_artist_id(self, access_token, artist_name):
        url = "https://api.spotify.com/v1/search?q={}&type=artist".format(artist_name)
        headers = {
            "Authorization": "Bearer {}".format(access_token)
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            artist_id = response_json["artists"]["items"][0]["id"]
            print("Artist ID for {}: {}".format(artist_name, artist_id))
            return artist_id
        else:
            print("Error getting artist ID: {}".format(response.text))

    def follow_artist(self, artist_name):
        global user_email
        access_token = self.get_token_in_db(user_email)
        artist_id = self.get_artist_id(access_token, artist_name)
        url = "https://api.spotify.com/v1/me/following?type=artist&ids={}".format(artist_id)
        headers = {
            "Authorization": "Bearer {}".format(access_token)
        }
        print (url)
        response = requests.put(url, headers=headers)

        if response.status_code == 204:
            print("You are now following the artist.")
        else:
            print("Error following artist: {}".format(response.text))

    def get(self, request):
        access_token,_, _ = self.get_authorization_code(request)
        # self.follow_artist(self.user_email, artist_name)
        return Response({'msg', 'getting auth code'})