from django.shortcuts import render
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseBadRequest
from rest_framework import generics, status
from areaServer.utils import Util
from rest_framework.response import Response
import os
from .serializers import SpotifySerializer
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
import json
from areaServer.models import User

# Create your views here.

# oauth_token = ''
# song_name = "it's you"
user_email = None
playlist_name = "Youtube Liked Songs"

class spotify_webhookAPIView(generics.GenericAPIView):
    serializer_class = SpotifySerializer

    client_id = os.environ.get('AREA_SPOTIFY_ID')
    client_secret = os.environ.get('AREA_SPOTIFY_SECRET')
    redirect_uri = 'http://127.0.0.1:8000/spotifyyy_app_playlist/'
    scope = "playlist-modify-private", "playlist-modify-public", "user-library-read", "user-read-private", "user-library-modify", "playlist-read-private", "playlist-read-collaborative", "user-follow-modify", "user-read-email"
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
        print (response.json())
        oauth_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]

        url = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization": "Bearer {}".format(oauth_token)
        }
        response = requests.get(url, headers=headers)
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
    
    def get_token_in_db(self, user_email):
        user = User.objects.filter(email=user_email).first()
        oauth_token = user.spotify_tokens["spotify_access_token"]
        return oauth_token
        
    def get_song_uri(self, user_email, song_name):
        oauth_token = self.get_token_in_db(self, user_email)
        # oauth_token = self.get_authorization_code(request)
        response = requests.get("https://api.spotify.com/v1/search?q={}&type=track".format(song_name),
                        headers={"Authorization": "Bearer {}".format(oauth_token)})
        if response.status_code == 200:
            response_json = response.json()
            try:
                song_uri = response_json["tracks"]["items"][0]["uri"]
            except:
                return HttpResponseBadRequest("Check that song exits in spotify", 400)
            print("Spotify URI for {}: {}".format(song_name, song_uri))
            return song_uri
        else:
            print("Error: {}".format(response.status_code))
            return ("Error: {}".format(response.status_code))

    def get_user_id(self, user_email):
        access_token = self.get_token_in_db(self, user_email)
        # access_token = self.get_authorization_code(request)
        response = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": "Bearer {}".format(access_token)})

        if response.status_code == 200:
            response_json = response.json()
            user_id = response_json["id"]
            print("User ID: {}".format(user_id))
            return user_id
        else:
            print("Error: {}".format(response.status_code))

    def create_playlist(self, user_email, user_id):
        access_token = self.get_token_in_db(self, user_email)
        # Step 1: Create an empty playlist and get its ID
        url = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)
        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "name": playlist_name,
            "public": False
        })
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 201:
            playlist_id = response.json()['id']
            print("Playlist created with ID: {}".format(playlist_id))
            return playlist_id
        else:
            print("Error creating playlist: {}".format(response.text))

    def add_song_to_playlist(self, song_name):
        global user_email
        access_token = self.get_token_in_db(self, user_email)
        playlist_id = None
        song_uri = self.get_song_uri(access_token, song_name)
        user_id = self.get_user_id(access_token)
        response = requests.get("https://api.spotify.com/v1/me/playlists",
                        headers={"Authorization": "Bearer {}".format(access_token)})
        if response.status_code == 200:
            response_json = response.json()
            for playlist in response_json["items"]:
                if playlist["name"] == playlist_name:
                    playlist_id = playlist["id"]
                    break
            if not playlist_id:
                playlist_id = self.create_playlist(access_token, user_id)            
        else:
            print("Error: {}".format(response.status_code))
            return HttpResponseBadRequest("could not find playlist", 400)

        response = requests.post("https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id),
                                json={"uris": [song_uri]},
                                headers={"Authorization": "Bearer {}".format(access_token),
                                        "Content-Type": "application/json"})
        if response.status_code == 201:
            print("Song added to Youtube Liked Songs")
        else:
            print("Error: {}".format(response.status_code))

    def get(self, request):
        self.get_authorization_code(self, request)
        return Response({'msg', 'getting auth code'})