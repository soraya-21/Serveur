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
import base64
import requests
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# Create your views here.
user_email = None
DEMO_KEY = os.environ.get('NASA_API_KEY')
scheduler = BackgroundScheduler()
scheduler.start()
ngrok_uri = ""
def get_token_in_db(user_email):
    user = User.objects.filter(email=user_email).first()
    oauth_token = user.slack_token
    return oauth_token

class slack_news_webhookAPIView(generics.GenericAPIView):
    serializer_class = slackSerializer

    client_id = os.environ.get('AREA_SLACK_ID')
    client_secret = os.environ.get('AREA_SLACK_SECRET')
    
    def __init__(self):
        # scheduler.add_job(self.post_message, 'interval', seconds=30)
        scheduler.add_job(self.post_message, trigger=IntervalTrigger(hours=24))
    
    def get_apod(self):
        response = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={DEMO_KEY}")
        print(response.json())
        apod_data = {
            "explanation" : response.json()['explanation'],
            "image_url" : response.json()['url'],
            "title" : response.json()['title']
        }
        return apod_data

    def get_token(self, request):
        if request.method == "POST":
            try:
                reponse_data = {
                    "user_email": request.POST.get('user_email'),
                    # "code": request.GET.get('code'),
                }
            except:
                print("No email found", status=400)
            print(reponse_data)
            global user_email
            user_email = reponse_data['user_email']
        if request.method == "GET":
            try:
                reponse_data = {
                    # "user_email": request.GET.get('user_email'),
                    "code": request.GET.get('code'),
                }
            except:
                print("No code found", status=400)
            print(reponse_data)
            print(f"code ====> {reponse_data['code']}")
            token_endpoint = "https://slack.com/api/oauth.v2.access"
            auth_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": reponse_data["code"],
                "redirect_uri": f'{ngrok_uri}/slack_app/news'
            }
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(token_endpoint, data=auth_data, headers=headers)
            if not reponse_data['code'] and not user_email:
                return HttpResponse("No code or email found", status=400)
            if response.status_code == 200:
                print(f"reponse ====> {response.json()}")
                try:
                    access_token = response.json()["access_token"]
                except:
                    return "could not get access token"
                print(f"access_token ====> {access_token}")
            else:
                print(type(response))
                print(response.status_code)
            
            # global user_email
            # user_email = reponse_data['user_email']
            user = User.objects.filter(email=user_email).first()
            if not user:
                return ("User not in db")
            else:
                user.slack_token = access_token
                user.save()   

    def post_message(self):
        apod_data = self.get_apod()
        response = requests.get(apod_data['image_url'])
        image_data = response.content
        image_base64 = base64.b64encode(image_data).decode('ascii')
        attachment = {
            'fallback': 'Image attachment',
            "text": apod_data['title'],
            'image_url': apod_data['image_url'],
            'image_bytes': len(image_data),
            'image_base64': image_base64
        }
        text = apod_data['explanation']

        url = "https://slack.com/api/chat.postMessage"
        global user_email
        access_token = get_token_in_db(user_email)
        payload = {
            "channel": "#random",
            "text": text,
            "attachments":[attachment]
        }
        print(access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.ok:
            print("Message sent successfully!")
        else:
            print("Error sending message:", response.json()["error"])

    # def schedule_sending(self, request):    
    def get(self, request):
        """Pour les requetes GET"""
        self.get_token(request)
        scheduler.resume()
        # self.follow_artist(self.user_email, artist_name)
        return Response({'msg', 'getting auth code'})
    
    def post(self, request):
        self.get_token(request)
        return Response({'msg', 'getting auth code'})


class slack_click_up_webhookAPIView(generics.GenericAPIView):
    serializer_class = slackSerializer

    client_id = os.environ.get('AREA_SLACK_ID')
    client_secret = os.environ.get('AREA_SLACK_SECRET')

    def get_token(self, request):
        if request.method == "POST":
            try:
                reponse_data = {
                    "user_email": request.POST.get('user_email'),
                    # "code": request.GET.get('code'),
                }
            except:
                print("No email found", status=400)
            print(reponse_data)
            global user_email
            user_email = reponse_data['user_email']
        if request.method == "GET":
            try:
                reponse_data = {
                    # "user_email": request.GET.get('user_email'),
                    "code": request.GET.get('code'),
                }
            except:
                print("No code found", status=400)
            print(reponse_data)
            print(f"code ====> {reponse_data['code']}")
            token_endpoint = "https://slack.com/api/oauth.v2.access"
            auth_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": reponse_data["code"],
                "redirect_uri": f'{ngrok_uri}/slack_app/send_created_task'
            }
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(token_endpoint, data=auth_data, headers=headers)
            if not reponse_data['code'] and not user_email:
                return HttpResponse("No code or email found", status=400)
            if response.status_code == 200:
                print(f"reponse ====> {response.json()}")
                try:
                    access_token = response.json()["access_token"]
                except:
                    return "could not get access token"
                print(f"access_token ====> {access_token}")
            else:
                print(type(response))
                print(response.status_code)
            
            user = User.objects.filter(email=user_email).first()
            if not user:
                return ("User not in db")
            else:
                user.slack_token = access_token
                user.save()

    def post_message(user_email, text):
        url = "https://slack.com/api/chat.postMessage"
        access_token = get_token_in_db(user_email)
        # print(post_message)
        payload = {
            "channel": "#general",
            "text": text,
        }
        print(access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.ok:
            print("Message sent successfully!")
        else:
            print("Error sending message:", response.json()["error"])

    def get(self, request):
        """Pour les requetes GET"""
        self.get_token(request)
        return Response({'msg', 'getting auth code'})