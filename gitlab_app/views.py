from django.shortcuts import render
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseBadRequest
from .gitlab_api import GitlabApi
from .notification import notify_user
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
from .serializers import GitlabSerializer
from areaServer.models import User

# Create your views here.

STATUS_RESOLVED = 'Resolved'
STATUS_PROGRESS = 'In_progress'

def get_token_in_db(self, user_email):
    user = User.objects.filter(email=user_email).first()
    oauth_token = user.gitlab_tokens["gitlab_access_token"]
    return oauth_token

def get_issue_title(self, project_id, issue_id, access_token):
    url = f"https://gitlab.com/api/v4/projects/{project_id}/issues/{issue_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        issue_info = response.json()
        title = issue_info["title"]
        return(title)
    else:
        return (None)

class Gitlab_push_webhookAPIView(generics.GenericAPIView):
    serializer_class = GitlabSerializer

    client_id = os.environ.get('AREA2_GITLAB_ID')
    client_secret = os.environ.get('AREA2_GITLAB_TOKEN')

    def push_event_webhook(self, request):
        if request.method == "GET":
            try:
                reponse_data = {
                    "code": request.GET.get('code')
                }
            except:
                return HttpResponse("No code found", status=400)
            print (reponse_data["code"])
            data = {
                'grant_type': 'authorization_code',
                'code': reponse_data["code"],
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': 'http://127.0.0.1:8000/gitlab-webhook/push_rea'
            }
            response = requests.post('https://gitlab.com/oauth/token', data=data)
            if response.status_code != 200:
                print(f'Error: {response.json()}')
            else:
                oauth_token = response.json()['access_token']
                refresh_token = response.json()["refresh_token"]
                print(f'Access token: {oauth_token}')
            url = 'https://gitlab.com/api/v4/user'
            # Send the request to the GitLab API
            response = requests.get(f'{url}?private_token={oauth_token}')

            # Parse the JSON response to get the user's email
            email = response.json()['email']
            user = User.objects.filter(email=email).first()
            if not user:
                return ("User not in db")
            else:
                user.gitlab_tokens = {
                    "gitlab_access_token" : oauth_token,
                    "gitlab_refresh_token" : refresh_token
                }
                user.save()
            gl = gitlab.Gitlab(url='https://gitlab.com', oauth_token=oauth_token)
            projects = gl.projects.list(owned=True)
            webhook_url = "https://9463-156-0-212-43.ngrok.io/gitlab-webhook/push_rea"
            for project in projects:
                hook = project.hooks.create({
                    'url': webhook_url,
                    'push_events': True,
                    'enable_ssl_verification': True
                })
                print(f'Webhook ajouté au projet {project.name} avec l\'URL {hook.url}')

    def send_push_email(self, request):
        if request.method == "POST":
            payload = request.data
            try:
                user_email = payload["user_email"]
            except:
                return HttpResponse("Couldn't get user email from payload")
            oauth_token = get_token_in_db(user_email)

            if payload['object_kind'] == 'push':
                repo_meta = {
                    'homepage': payload['repository']['homepage'],
                }
            else:
                return HttpResponseBadRequest("Unsupported object kind", 422)
            
            if payload['object_kind'] == 'push':
                try:
                    email_body= f'New push on {payload["project"]["name"]} on branch "{payload["ref"]}". Commit title was "{payload["commits"][0]["title"]}".\nModified files: ({payload["commits"][0]["modified"]}). You can access your commit using the link below {payload["commits"][0]["url"]}'
                    data = {
                        'email_subject':'Push notification on gitlab',
                        'email_body':email_body,
                        'to_email': payload['commits'][0]['author']['email']
                    }
                    Util.send_email(data)
                except:
                    return HttpResponseBadRequest("Couldn't send email", 422)

                return HttpResponse('OK', status=200)

    def get(self, request):
        self.push_event_webhook(request)
        return Response({'msg', 'getting auth code'})      

    def post(self, request):
        self.send_push_email(request)
        return Response({'msg', 'posting on webhooks'})

class Gitlab_MR_Opened_webhookAPIView(generics.GenericAPIView):
    serializer_class = GitlabSerializer

    client_id = os.environ.get('AREA2_GITLAB_ID')
    client_secret = os.environ.get('AREA2_GITLAB_TOKEN')

    def mr_opened_event_webhook(self, request):
        if request.method == "GET":
            try:
                reponse_data = {
                    "code": request.GET.get('code')
                }
            except:
                return HttpResponse("No code found", status=400)
            print (reponse_data["code"])
            data = {
                'grant_type': 'authorization_code',
                'code': reponse_data["code"],
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': 'http://127.0.0.1:8000/gitlab-webhook/mr_opened_rea'
            }
            response = requests.post('https://gitlab.com/oauth/token', data=data)
            if response.status_code != 200:
                print(f'Error: {response.json()}')
            else:
                oauth_token = response.json()['access_token']
                refresh_token = response.json()["refresh_token"]
                print(f'Access token: {oauth_token}')
            url = 'https://gitlab.com/api/v4/user'
            # Send the request to the GitLab API
            response = requests.get(f'{url}?private_token={oauth_token}')

            # Parse the JSON response to get the user's email
            email = response.json()['email']
            user = User.objects.filter(email=email).first()
            if not user:
                return ("User not in db")
            else:
                user.gitlab_tokens = {
                    "gitlab_access_token" : oauth_token,
                    "gitlab_refresh_token" : refresh_token
                }
                user.save()
            gl = gitlab.Gitlab(url='https://gitlab.com', oauth_token=oauth_token)
            projects = gl.projects.list(owned=True)
            webhook_url = "https://9463-156-0-212-43.ngrok.io/gitlab-webhook/mr_opened_rea"
            for project in projects:
                hook = project.hooks.create({
                    'url': webhook_url,
                    'merge_requests_events': True,
                    'enable_ssl_verification': True
                })
                print(f'Webhook ajouté au projet {project.name} avec l\'URL {hook.url}')

    # def get_token_in_db(self, user_email):
    #     user = User.objects.filter(email=user_email).first()
    #     oauth_token = user.gitlab_tokens["gitlab_access_token"]
    #     return oauth_token
    
    def label_status_loading(self, request):
        if request.method == "POST":
            payload = request.data
            try:
                user_email = payload["user"]["email"]
            except:
                return HttpResponse("Couldn't get user email from payload")
            oauth_token = get_token_in_db(user_email)
            if payload['object_kind'] == 'merge_request':
                repo_meta = {
                    'homepage': payload['repository']['homepage'],
                }
            else:
                return HttpResponseBadRequest("Unsupported object kind", 422)

            if payload['object_kind'] == 'merge_request':
                # gl = GitlabApi(repo_meta['homepage'], oauth_token)
                merge_status = payload['object_attributes']['state']
                project_id = payload['project']['id']
                source_branch = payload['object_attributes']['source_branch']
                target_branch = payload['object_attributes']['target_branch']
                try:
                    # Supported branch format: <issue_id>-branch_name
                    # The issue_id shoud be an integer 
                    issue_id = int(source_branch.split("-")[0])
                except:
                    return HttpResponseBadRequest("Unsupported branch format", 422)
                issue_title = get_issue_title(project_id, issue_id, oauth_token)

                if merge_status == "opened":
                    headers = {
                        "Authorization": f"Bearer {oauth_token}"
                    }
                    labels = [STATUS_PROGRESS]
                    r = requests.put(f"https://gitlab.com/api/v4/projects/{project_id}/issues/{issue_id}", headers=headers, data={'labels': labels})
                    if not r:
                        return HttpResponseBadRequest("Failed to set label", status=422)

                return HttpResponse('OK', status=200)

    def get(self, request):
        self.mr_opened_event_webhook(request)
        return Response({'msg', 'getting auth code'})
        

    def post(self, request):
        self.label_status_loading(request)
        return Response({'msg', 'posting on webhooks'})

class Gitlab_MR_Merged_Label_webhookAPIView(generics.GenericAPIView):
    serializer_class = GitlabSerializer

    client_id = os.environ.get('AREA2_GITLAB_ID')
    client_secret = os.environ.get('AREA2_GITLAB_TOKEN')

    def mr_merged_label_event_webhook(self, request):
        if request.method == "GET":
            try:
                reponse_data = {
                    "code": request.GET.get('code')
                }
            except:
                return HttpResponse("No code found", status=400)
            print (reponse_data["code"])
            data = {
                'grant_type': 'authorization_code',
                'code': reponse_data["code"],
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': 'http://127.0.0.1:8000/gitlab-webhook/change-label_rea'
            }
            response = requests.post('https://gitlab.com/oauth/token', data=data)
            if response.status_code != 200:
                print(f'Error: {response.json()}')
            else:
                oauth_token = response.json()['access_token']
                refresh_token = response.json()["refresh_token"]
                print(f'Access token: {oauth_token}')
            url = 'https://gitlab.com/api/v4/user'
            # Send the request to the GitLab API
            response = requests.get(f'{url}?private_token={oauth_token}')

            # Parse the JSON response to get the user's email
            email = response.json()['email']
            user = User.objects.filter(email=email).first()
            if not user:
                return ("User not in db")
            else:
                user.gitlab_tokens = {
                    "gitlab_access_token" : oauth_token,
                    "gitlab_refresh_token" : refresh_token
                }
                user.save()

            gl = gitlab.Gitlab(url='https://gitlab.com', oauth_token=oauth_token)
            projects = gl.projects.list(owned=True)
            webhook_url = "https://9463-156-0-212-43.ngrok.io/gitlab-webhook/change-label_rea"
            for project in projects:
                hook = project.hooks.create({
                    'url': webhook_url,
                    'merge_requests_events': True,
                    'enable_ssl_verification': True
                })
                print(f'Webhook ajouté au projet {project.name} avec l\'URL {hook.url}')
        
    def status_resolved_label(self, request):
        if request.method == "POST":
            payload = request.data
            try:
                user_email = payload["user"]["email"]
            except:
                return HttpResponse("Couldn't get user email from payload")
            oauth_token = get_token_in_db(user_email)
            if payload['object_kind'] == 'merge_request':
                repo_meta = {
                    'homepage': payload['repository']['homepage'],
                }
            else:
                return HttpResponseBadRequest("Unsupported object kind", 422)

            if payload['object_kind'] == 'merge_request':
                gl = GitlabApi(repo_meta['homepage'], oauth_token)
                merge_status = payload['object_attributes']['state']
                project_id = payload['project']['id']
                source_branch = payload['object_attributes']['source_branch']
                target_branch = payload['object_attributes']['target_branch']
                try:
                    # Supported branch format: <issue_id>-branch_name
                    # The issue_id shoud be an integer 
                    issue_id = int(source_branch.split("-")[0])
                except:
                    return HttpResponseBadRequest("Unsupported branch format", 422)
                issue_title = get_issue_title(project_id, issue_id, oauth_token)
                
                if merge_status == "merged":
                    labels = [STATUS_RESOLVED]
                    headers = {
                        "Authorization": f"Bearer {oauth_token}"
                    }
                    r = requests.put(f"https://gitlab.com/api/v4/projects/{project_id}/issues/{issue_id}", headers=headers, data={'labels': labels})

                    if not r:
                        return HttpResponseBadRequest("Failed to set label", status=422)

                return HttpResponse('OK', status=200)

    def get(self, request):
        self.mr_merged_label_event_webhook(request)
        return Response({'msg', 'getting auth code'})
        

    def post(self, request):
        self.status_resolved_label(request)
        return Response({'msg', 'posting on webhooks'})

class Gitlab_MR_Merged_Notif_webhookAPIView(generics.GenericAPIView):
    serializer_class = GitlabSerializer

    client_id = os.environ.get('AREA2_GITLAB_ID')
    client_secret = os.environ.get('AREA2_GITLAB_TOKEN')

    def mr_merged_notif_event_webhook(self, request):
        if request.method == "GET":
            try:
                reponse_data = {
                    "code": request.GET.get('code')
                }
            except:
                return HttpResponse("No code found", status=400)
            print (reponse_data["code"])
            data = {
                'grant_type': 'authorization_code',
                'code': reponse_data["code"],
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': 'http://127.0.0.1:8000/gitlab-webhook/merged-notif_rea'
            }
            response = requests.post('https://gitlab.com/oauth/token', data=data)
            if response.status_code != 200:
                print(f'Error: {response.json()}')
            else:
                oauth_token = response.json()['access_token']
                refresh_token = response.json()["refresh_token"]
                print(f'Access token: {oauth_token}')
            url = 'https://gitlab.com/api/v4/user'
            # Send the request to the GitLab API
            response = requests.get(f'{url}?private_token={oauth_token}')

            # Parse the JSON response to get the user's email
            email = response.json()['email']
            user = User.objects.filter(email=email).first()
            if not user:
                return ("User not in db")
            else:
                user.gitlab_tokens = {
                    "gitlab_access_token" : oauth_token,
                    "gitlab_refresh_token" : refresh_token
                }
                user.save()

            gl = gitlab.Gitlab(url='https://gitlab.com', oauth_token=oauth_token)
            projects = gl.projects.list(owned=True)
            webhook_url = "https://9463-156-0-212-43.ngrok.io/gitlab-webhook/merged-notif_rea"
            for project in projects:
                hook = project.hooks.create({
                    'url': webhook_url,
                    'merge_requests_events': True,
                    'enable_ssl_verification': True
                })
                print(f'Webhook ajouté au projet {project.name} avec l\'URL {hook.url}')

    def send_merged_email(self, request):
        if request.method == "POST":
            payload = request.data
            try:
                user_email = payload["user"]["email"]
            except:
                return HttpResponse("Couldn't get user email from payload")
            oauth_token = get_token_in_db(user_email)

            if payload['object_kind'] == 'merge_request':
                repo_meta = {
                    'homepage': payload['repository']['homepage'],
                }
            else:
                return HttpResponseBadRequest("Unsupported object kind", 422)

            if payload['object_kind'] == 'merge_request':
                # gl = GitlabApi(repo_meta['homepage'], oauth_token)
                merge_status = payload['object_attributes']['state']
                project_id = payload['project']['id']
                source_branch = payload['object_attributes']['source_branch']
                target_branch = payload['object_attributes']['target_branch']
                try:
                    # Supported branch format: <issue_id>-branch_name
                    # The issue_id shoud be an integer 
                    issue_id = int(source_branch.split("-")[0])
                except:
                    return HttpResponseBadRequest("Unsupported branch format", 422)
                issue_title = get_issue_title(project_id, issue_id, oauth_token)
                
                if merge_status == "merged":
                    author_name = payload['object_attributes']['last_commit']['author']['name']

                    if author_name and issue_title:
                        email_body = f'Merge request resolving issue "{issue_title}" accepted by {payload["user"]["name"]} on branch {target_branch}\nAccess your project on the link below {payload["object_attributes"]["target"]["web_url"]}'
                        data = {
                            'email_subject':'Merge notification on gitlab',
                            'email_body':email_body,
                            'to_email': payload['object_attributes']['last_commit']['author']['email']
                        }
                        Util.send_email(data)
                        print(f"MR deployée @{author_name}")
                    else:
                        return HttpResponseBadRequest("Failed to get username", 422)

                return HttpResponse('OK', status=200)

    def get(self, request):
        self.mr_merged_notif_event_webhook(request)
        return Response({'msg', 'getting auth code'})
        

    def post(self, request):
        self.send_merged_email(request)
        return Response({'msg', 'posting on webhooks'})
