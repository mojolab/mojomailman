from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import Context
from mailusers.models import *
@login_required
def index(request):
	c=Context()
	emailaddresses=EmailAddress.objects.all().filter(user__username=request.user.username)
	c['emailaddresses']=emailaddresses
	print c
	return render(request,"mailusers/index.html",c)

# Create your views here.
