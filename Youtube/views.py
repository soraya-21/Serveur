from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest, JsonResponse
import ipaddress
import json
import argparse
import io
import os
import gitlab
import requests
import xml.etree.cElementTree as ET
from rest_framework import generics, status
from google.auth.transport.requests import Request
from areaServer.utils import Util
from rest_framework.response import Response
from .serializers import YoutubeSerializer
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from google_auth_oauthlib.flow import Flow
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect, render
from django.urls import reverse
from . import settings
from google.oauth2 import id_token
from .models import User
import json
from linkedin_app.views import Linkedin_webhookAPIView


# Create your views here.

client_secrets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')

with open(client_secrets_file, "r") as json_file:
    client_secrets = json.load(json_file)

flow = Flow.from_client_config(
    client_config=client_secrets,
    scopes=['https://www.googleapis.com/auth/youtube.force-ssl', 'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile', 'openid'],
    redirect_uri='http://localhost:8000/youtube_/oauth2callback'
)

def credentials_to_dict(credentials):
    """
    Convertit un objet Credentials en un dictionnaire.

    Le dictionnaire contient les informations d'identification suivantes :
    - token: le jeton d'accès OAuth 2.0
    - refresh_token: le jeton de rafraîchissement OAuth 2.0
    - token_uri: l'URI du point de terminaison OAuth 2.0 pour les jetons d'accès
    - client_id: l'ID client OAuth 2.0
    - client_secret: le secret client OAuth 2.0
    - scopes: les portées autorisées pour le jeton d'accès
    """
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
# Création d'une vue Django pour l'authentification

def like_video(request):
    credentials_dict = request.session.get('credentials')
    if credentials_dict is None:
        return redirect('login')

    credentials = Credentials.from_authorized_user_info(info=credentials_dict)

    #try:
    youtube = build('youtube', 'v3', credentials=credentials)
    response = youtube.videos().list(
        part='snippet',
        myRating='like',
        maxResults=1
    ).execute()

    for item in response['items']:
        print(item['snippet']['title'])
    return HttpResponse('Video liked!')

def login(request):
    authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
    request.session['state'] = state
    return redirect(authorization_url)

def oauth2callback(request):
    code = request.GET.get('code')
    flow.fetch_token(code=code)
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    access_token = credentials.token
    
    oauth2_client = build('oauth2', 'v2', credentials=credentials)
    user_info = oauth2_client.userinfo().get().execute()
    email = user_info['email']

    user, created = User.objects.get_or_create(email=email)

    # request.session['youtube_credentials'] = credentials.to_json()
    request.session['user_id'] = user.id
    #get_last_liked_video_id(access_token)
    #print(json.dumps(response, indent=4))
    #return HttpResponse("ok")
    return redirect('http://localhost:5173/youtube')

def get_subsriptions(request):
    credentials_dict = request.session.get('credentials')
    if credentials_dict is None:
        return redirect('login')

    credentials = Credentials.from_authorized_user_info(info=credentials_dict)
    youtube = build('youtube', 'v3', credentials=credentials)

    # Définir les paramètres de la requête
    my_subscription = None
    next_page_token = None

    # Récupérer les abonnements de l'utilisateur et les trier par date de souscription
    while True:
        try:
            # Appeler la méthode subscriptions().list() de l'API YouTube Data v3
            subscriptions_response = youtube.subscriptions().list(
                part='snippet',
                mine=True,
                pageToken=next_page_token,
                order='alphabetical',  # Cette ligne est ajoutée pour trier les abonnements par ordre alphabétique. Vous pouvez la retirer si vous ne voulez pas trier les abonnements.
                maxResults=50
            ).execute()

            # Trier les abonnements par date de souscription en ordre décroissant
            subscriptions = sorted(subscriptions_response['items'], key=lambda x: x['snippet']['publishedAt'], reverse=True)

            # Récupérer le dernier abonnement
            if subscriptions:
                my_subscription = subscriptions[0]
                break

            # Vérifier s'il y a une page suivante
            next_page_token = subscriptions_response.get('nextPageToken')
            if not next_page_token:
                break

        except HttpError as error:
            print('Une erreur est survenue : %s' % error)
            break

    # Afficher le titre du dernier abonnement de l'utilisateur
    if my_subscription:
        print(my_subscription['snippet']['title'])
    return HttpResponse("ok")
#     # Vérifier que l'utilisateur est connecté
#     if not request.user.is_authenticated:
#         return render(request, 'error.html', {'error_message': 'Vous devez être connecté pour utiliser cette fonctionnalité.'})

#     # Récupérer les identifiants d'authentification de l'utilisateur
#     user_credentials = Credentials.from_authorized_user_info(request.user.social_auth.get(provider='google-oauth2').extra_data)

#     # Vérifier si les identifiants d'authentification ont expiré
#     if user_credentials.expired and user_credentials.refresh_token:
#         user_credentials.refresh(requests.Request())

#     # Créer un objet de service pour l'API YouTube Data v3
#     youtube = build('youtube', 'v3', credentials=user_credentials)

#     # Appeler l'API YouTube Data v3 pour récupérer les vidéos likées de l'utilisateur
#     response = youtube.videos().list(
#         part='snippet',
#         myRating='like'
#     ).execute()

#     # Récupérer le titre de la dernière vidéo likée de l'utilisateur
#     if 'items' in response and len(response['items']) > 0:
#         latest_liked_video = response['items'][0]
#         video_title = latest_liked_video['snippet']['title']
#         return render(request, 'liked_video_title.html', {'video_title': video_title})
#     else:
#         return render(request, 'error.html', {'error_message': 'Aucune vidéo likée trouvée.'})

class Youtube_webhookAPIView(generics.GenericAPIView):
    http_method_names = ['get', 'post']
    serializer_class = YoutubeSerializer

#     client_id = os.environ.get(
#         '925779292051-dlogeud1h4ks9u5t7p0go9qi5i79cefr.apps.googleusercontent.com')
#     client_secret = os.environ.get('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')
#     API_ENDPOINT = 'https://oauth2.googleapis.com/token'

#     def pipeline_webhook(self, request):
#         if request.method == "GET":
#             try:
#                 reponse_data = {
#                     "code": request.GET.get('code')
#                 }
#             except:
#                 return HttpResponse("No code found", status=400)
#             print(reponse_data["code"])
#             data = {
#                 'client_id': self.client_id,
#                 'client_secret': self.client_secret,
#                 'grant_type': 'authorization_code',
#                 'code': reponse_data["code"],
#                 'redirect_uri': 'http://127.0.0.1:8000/youtube_/',
#             }
#             headers = {
#                 'Content-Type': 'application/x-www-form-urlencoded'
#             }
#             print(data)
#             response = requests.post(
#                 f'{self.API_ENDPOINT}/oauth2/token', data=data, headers=headers)
#             #print(response.json)

#         return HttpResponse("ok")

#             # response.raise_for_status()
#             # print(response.json())
#             # if response.status_code == 200:
#             #     # Parse the response JSON and extract the access token
#             #     response_json = response.json()
#             #     print(response_json)
#             #     access_token = response_json["access_token"]
#             #     print(f'Access token: {access_token}')

#             # else:
#             #     return HttpResponse("Could not get access token", status=response.status_code)
#     def get_last_liked_video_id(access_token):
#         youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY_HERE', access_token=access_token)
#         try:
#             response = youtube.activities().list(
#                 part='contentDetails',
#                 mine=True,
#                 maxResults=1,
#                 fields='items(contentDetails/like/resourceId/videoId)'
#             ).execute()
#             return response['items'][0]['contentDetails']['like']['resourceId']['videoId']
#         except HttpError as error:
#             print(f'An error occurred: {error}')


    def get(self, request):
        if 'hub.challenge' in request.GET:
            return HttpResponse(request.GET['hub.challenge'], content_type='text/plain')
        #self.pipeline_webhook(request)
        return HttpResponse()

    def post(self, request):
        if request.method == 'POST':
            xml_content = request.body.decode('utf-8')
            tree = ET.ElementTree(ET.fromstring(xml_content))
            # Trouver la balise 'entry'
            entry = tree.find('{http://www.w3.org/2005/Atom}entry')
            # Trouver le titre
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            link = entry.find("{http://www.w3.org/2005/Atom}link")
            video_link = link.get("href")
            print(video_link)
            print(title)
            Linkedin_webhookAPIView.send_post(title, video_link)
            return HttpResponse(title, video_link)