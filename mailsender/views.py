from google.oauth2 import credentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
import os, sys
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Définir les portées pour l'accès à l'API Gmail
# SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.modify']
# client_id = os.environ.get('GOOGLE_CLIENT_ID')
# client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
# # Définir le nom du fichier de sauvegarde des jetons d'accès
# TOKEN_FILE = 'token.json'

# # Définir le nom du fichier contenant les informations d'identification de l'application OAuth2
# CLIENT_SECRET_FILE = 'client_secrets.json'

# # Définir l'URL de redirection
# REDIRECT_URI = 'http://127.0.0.1:8000/mailsender/'


def mail_sender(a=0):
    pass
#     flow = InstalledAppFlow.from_client_config(
#         client_config={"web":{"client_id":"988782552823-38nfdbo9naqi8jcpdtar6o0di5go90d1.apps.googleusercontent.com","project_id":"areaserver-375309","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["http://127.0.0.1:8000/mailsender/","http://127.0.0.1:8000/"]}},
#         scopes=SCOPES)

#     credentials = flow.run_local_server(host= "127.0.0.1",port=8000)

#     print('Success. Your token is:\n', credentials.token)

#     try:
#         # create gmail api client
#         service = build('gmail', 'v1', credentials=credentials)

#         message = EmailMessage()

#         message.set_content('Petit con')

#         message['To'] = 'soraya.codo@epitech.eu'
#         message['From'] = 'area_get_skills@areaepitech.eu'
#         message['Subject'] = 'test'

#         # encoded message
#         encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
#             .decode()

#         create_message = {
#             'raw': encoded_message
#         }
#         # pylint: disable=E1101
#         send_message = (service.users().messages().send
#                         (userId="me", body=create_message).execute())
#         print(F'Message Id: {send_message["id"]}')
#         profile = service.users().getProfile(userId='me').execute()
#         email = profile['emailAddress']

#         print(f"User email address: {email}")
#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         send_message = None
#     return send_message

# mail_sender()