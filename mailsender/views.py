from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    if request.method == "GET":
        sub = request.GET.get('subject')
        msg = request.GET.get('message')
        email = request.GET.get('email')
        print(sub, msg, email)
        return HttpResponse('email send that !')
    return render(request, 'mailsender/form.html')