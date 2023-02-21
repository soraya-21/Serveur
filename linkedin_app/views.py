from django.shortcuts import render
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseBadRequest
import ipaddress
import json
import argparse
import io
import os
import gitlab
import requests
from rest_framework import generics, status
from areaServer.utils import Util
from rest_framework.response import Response
import os
from .serializers import LinkedinSerializer
from areaServer.models import User

# Create your views here.

oauth_token = ''
user_email = "soraya.codo@epitech.eu"
API_ENDPOINT = "https://www.linkedin.com"

class Linkedin_webhookAPIView(generics.GenericAPIView):
    serializer_class = LinkedinSerializer

    client_id = os.environ.get('AREA_LINKEDIN_ID')
    client_secret = os.environ.get('AREA_LINKEDIN_TOKEN')

    def get_token(self, request):
        if request.method == "GET":
            try:
                reponse_data = {
                    "code": request.GET.get('code')
                }
            except:
                return HttpResponse("No code found", status=400)
            data = {
                'grant_type': 'authorization_code',
                'code': reponse_data["code"],
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': 'http://127.0.0.1:8000/linkedin_app/'
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(f'{API_ENDPOINT}/oauth/v2/accessToken', data=data, headers=headers)
            if response.status_code != 200:
                return HttpResponse(f'Error: {response.json()}')
            else:
                oauth_token = response.json()["access_token"]
                # url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"

                # headers = {
                #     "Authorization": f"Bearer {oauth_token}",
                #     "Content-Type": "application/json",
                #     "X-Restli-Protocol-Version": "2.0.0"
                # }
                # response = requests.get(url, headers=headers)
                # if response.status_code == 200:
                #     data = json.loads(response.content)
                #     email = data["elements"][0]["handle~"]["emailAddress"]
                #     print("L'e-mail de l'utilisateur est :", email)
                # else:
                #     return HttpResponse("Erreur lors de la récupération de l'e-mail de l'utilisateur :", response.json())
                # user = User.objects.filter(email=email).first()
                # if not user:
                #     return ("User not in db")
                # else:
                #     user.linkedin_token = oauth_token
                #     user.save()
            return oauth_token

    def get_urn_id(self, access_token):
        url = "https://api.linkedin.com/v2/me"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = json.loads(response.content)
            urn_id = data["id"]
            print("Votre urn_id LinkedIn est :", urn_id)
        else:
            return HttpResponse("Erreur lors de la récupération de l'urn_id :", response.json())
        return urn_id

    def send_post(self, access_token, description, video_link):
        urn_id = self.get_urn_id(access_token)
        introdute_link = "Vous trouverez la video au lien suivant :"
        url = "https://api.linkedin.com/v2/ugcPosts"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        data = {
            "author": f"urn:li:person:{urn_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": f"{description}\n {introdute_link}\n{video_link}"
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            print("Le post a été publié avec succès !")
        else:
            return HttpResponse("Erreur lors de la publication du post :", response.json())


    def get_token_in_db(self, user_email):
        user = User.objects.filter(email=user_email).first()
        oauth_token = user.spotify_tokens["linkedin_token"]
        return oauth_token

    def get(self, request):
        description = "blablabla description de la video"
        video_link = "https://www.hahahaha.com"
        access_token = self.get_token(request)
        self.send_post(access_token, description, video_link)
        return Response({'msg', 'getting auth code'})        

    def post(self, request):
        return Response({'msg', 'posting on webhooks'})