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

# Create your views here.

class slack_webhookAPIView(generics.GenericAPIView):
    serializer_class = slackSerializer
    