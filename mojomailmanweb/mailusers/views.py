from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import Context
from mailusers.models import *
from datetime import *	

# Create your views here.

@login_required
def index(request):
	c=Context()
	
	
	objects=EmailAddress.objects.all().filter(user__username=request.user.username)
	emailaddresses=[]
	for emailaddress in objects:
		dictionary={}
		dictionary['email']=emailaddress.email
		dictionary['queued']=emailaddress.num_emails_queued
		dictionary['new']=emailaddress.num_new_emails
		dictionary['lastchecked']=emailaddress.last_modified.strftime("%Y-%b-%d %H:%M:%S %Z")
		emailaddresses.append(dictionary)
	
	c['emailaddresses']=emailaddresses
	
	print c
	y= emailaddresses
	context ={'x':y}
	return render(request,"mailusers/index.html",context)
def test(request,num):
	dictionary={}
	dictionary['req']=request
	dictionary['num']=num
	emaildetail=get_object_or_404(EmailAddress, pk=num)
	print emaildetail
	dictionary['detail']=emaildetail
	return render(request,"mailusers/test.html",dictionary)
def generate_email_config(request,num):
	dictionary={}
	dictionary['req']=request
	dictionary['num']=num
	emaildetail=get_object_or_404(EmailAddress, pk=num)
	print emaildetail
	dictionary['detail']=emaildetail
	return render(request,"mailusers/test.html",dictionary)
def view_email_config(request,num):
	dictionary={}
	dictionary['req']=request
	dictionary['num']=num
	emaildetail=get_object_or_404(EmailAddress, pk=num)
	print emaildetail
	dictionary['detail']=emaildetail
	return render(request,"mailusers/test.html",dictionary)
def apply_email_config(request,num):
	dictionary={}
	dictionary['req']=request
	dictionary['num']=num
	emaildetail=get_object_or_404(EmailAddress, pk=num)
	print emaildetail
	dictionary['detail']=emaildetail
	return render(request,"mailusers/test.html",dictionary)
