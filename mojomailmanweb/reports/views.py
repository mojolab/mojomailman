from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

def index(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/mailusers/")
	else:
		return render(request,"reports/index.html")
  
