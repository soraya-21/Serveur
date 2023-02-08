"""
WSGI config for djangoAPI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoAPI.settings')

application = get_wsgi_application()

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coffee.settings")
# Remember to change coffe.settings to your_project_name.settings

application = get_wsgi_application()
application = WhiteNoise(application)