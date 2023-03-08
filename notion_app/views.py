from django.shortcuts import render
from .serializers import notionSerializer
from django.shortcuts import render
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseBadRequest
from rest_framework import generics, status
from areaServer.utils import Util
from rest_framework.response import Response
import os
from areaServer.models import User
import requests
import base64
import json
from slack_app.views import slack_click_up_webhookAPIView

user_email = None
ngrok_uri = "https://252a-154-66-134-64.eu.ngrok.io"
# Create your views here.
def get_token_in_db(user_email):
    user = User.objects.filter(email=user_email).first()
    oauth_token = user.click_up_token
    return oauth_token

class notion_webhookAPIView(generics.GenericAPIView):
    serializer_class = notionSerializer
    
    client_id = os.environ.get('CLICK_UP_CLIENT_ID')
    client_secret = os.environ.get('CLICK_UP_CLIENT_SECRET')

    def get_token(self, request):
        if request.method == "GET":
            try:
                reponse_data = {
                    "code": request.GET.get('code'),
                }
            except:
                return HttpResponse("No code found", status=400)
            print(f"code ====> {reponse_data['code']}")
            
            url = "https://api.clickup.com/api/v2/oauth/token"

            query = {
            "client_id": self.client_id ,
            "client_secret": self.client_secret ,
            "code": reponse_data['code']
            }

            response = requests.post(url, params=query)

            data = response.json()
            print(data)
            try:
                access_token = data['access_token']
                print(f"access_token ===> {access_token}")
            except:
                print(f"ERROR====>{response.content}")

            url = "https://api.clickup.com/api/v2/user"
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.get(url, headers=headers)
            data = response.json()

            email = data['user']["email"]
            global user_email
            user_email = email

            user = User.objects.filter(email=email).first()
            if not user:
                return ("User not in db")
            else:
                user.click_up_token = access_token
                user.save()

            url = "https://api.clickup.com/api/v2/team"

            headers = {
                "Authorization": access_token
            }

            response = requests.get(url, headers=headers)

            if response.ok:
                data = response.json()["teams"]
                team_ids = [team["id"] for team in data]
                print("Team IDs:", team_ids)
            else:
                print("Failed to get teams")
                print(response.text)
            
            self.add_webhook(access_token, team_ids)

    def add_webhook(self, access_token, team_ids):
        for team_id in team_ids:
            url = f"https://api.clickup.com/api/v2/team/{team_id}/webhook"
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            data = {
                "endpoint": f"{ngrok_uri}/notion_app/",
                "events": [
                    "taskCreated"
                ]
            }

            response = requests.post(url, headers=headers, json=data)

            if response.ok:
                print("Webhook créé avec succès")
            else:
                print("Failed to create webhook")
                print(response.text)
    
    def get_information_from_webhook(self, payload):
        if payload['event'] == "taskCreated":
            global user_email
            access_token = get_token_in_db(user_email)
            task_id = payload['task_id']
            headers = {"Authorization": access_token}

            # Send the request to the API
            response = requests.get(f"https://api.clickup.com/api/v2/task/{task_id}", headers=headers)

            # Get the JSON response and print it
            task_info = response.json()
            print(json.dumps(task_info))
            task_name = task_info['name']
            task_creator = task_info['creator']['username']
            task_list = task_info['list']['name']
            task_url = task_info['url']
            message_text = f'A task named "{task_name}" have just been created by {task_creator} in {task_list}. Find here link to it: {task_url}'
            slack_click_up_webhookAPIView.post_message(user_email, message_text)


    def get(self, request):
        """Pour les requetes GET"""
        self.get_token(request)
        return Response({'msg', 'getting auth code'})
    
    def post(self, request):
        """Pour les requetes GET"""
        if request.method == "POST":
            payload = request.data
            print(json.dumps(payload))
            self.get_information_from_webhook(payload)
        return Response({'msg', 'getting auth code'})