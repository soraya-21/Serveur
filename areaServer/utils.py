from django.core.mail import EmailMessage
import jwt
from django.conf import settings

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()

    
    def generate_jwt(email):
        payload = {
            'email': email,
            'token_type': 'access',
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token