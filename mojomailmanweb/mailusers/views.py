from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request,"mailusers/index.html")

# Create your views here.
