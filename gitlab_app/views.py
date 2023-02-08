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

# Create your views here.
import hashlib
from base64 import urlsafe_b64encode, urlsafe_b64decode
import base64
import os

STATUS_RESOLVED = 'Resolved'
STATUS_PROGRESS = 'In_progress'

oauth_token = ''
class Gitlab_webhookAPIView(generics.GenericAPIView):
    client_id = os.environ.get('AREA2_GITLAB_ID')
    client_secret = os.environ.get('AREA2_GITLAB_TOKEN')

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

    def pipeline_webhook(self, request):
        if request.method == "GET":
            try:
                reponse_data = {
                    "code": request.GET.get('code')
                }
                data = {
                    'grant_type': 'authorization_code',
                    'code': reponse_data("code"),
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': 'https://127.0.0.1:8000/gitlab-webhook/'
                }
                response = requests.post('https://gitlab.com/oauth/token', data=data)
                if response.status_code != 200:
                    print(f'Error: {response.json()}')
                else:
                    oauth_token = response.json()['access_token']
                    print(f'Access token: {oauth_token}')
                gl = gitlab.Gitlab(url='https://gitlab.com', oauth_token=oauth_token)
                projects = gl.projects.list(owned=True)
                webhook_url = "https://a2d6-197-234-221-22.eu.ngrok.io/gitlab-webhook/"
                for project in projects:
                    hook = project.hooks.create({
                        'url': webhook_url,
                        'push_events': True,
                        'merge_requests_events': True,
                        'pipeline_events': True,
                        'enable_ssl_verification': True
                    })
                    print(f'Webhook ajouté au projet {project.name} avec l\'URL {hook.url}')
            except:
                return HttpResponse("No code found", status=400)
        elif request.method == "POST":
            payload = request.data

            if payload['object_kind'] in ['merge_request', 'push']:
                repo_meta = {
                    'homepage': payload['repository']['homepage'],
                }
            elif payload['object_kind'] == 'pipeline':
                repo_meta = {
                    'homepage': payload['project']['web_url'],
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
                issue_title = self.get_issue_title(project_id, issue_id, oauth_token)

                if merge_status == "opened":
                    headers = {
                        "Authorization": f"Bearer {oauth_token}"
                    }
                    labels = [STATUS_PROGRESS]
                    r = requests.put(f"https://gitlab.com/api/v4/projects/{project_id}/issues/{issue_id}", headers=headers, data={'labels': labels})
                    if not r:
                        return HttpResponseBadRequest("Failed to set label", status=422)
                
                if merge_status == "merged":
                    labels = [STATUS_RESOLVED]
                    headers = {
                        "Authorization": f"Bearer {oauth_token}"
                    }
                    r = requests.put(f"https://gitlab.com/api/v4/projects/{project_id}/issues/{issue_id}", headers=headers, data={'labels': labels})

                    if not r:
                        return HttpResponseBadRequest("Failed to set label", status=422)

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
        self.pipeline_webhook(request)
        return Response({'msg', 'getting auth code'})
        

    def post(self, request):
        self.pipeline_webhook(request)
        return Response({'msg', 'posting on webhooks'})
