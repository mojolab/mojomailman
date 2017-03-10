from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser,User

# Create your models here.

class EmailAddress(models.Model):
	user = models.ForeignKey(User)
	email = models.CharField(max_length=255,null=False, blank=False,unique=True)
	password = models.CharField(max_length=255,null=True, blank=True)
	email_smtp_server = models.CharField(max_length=255,null=True, blank=True)
	email_smtp_port = models.CharField(max_length=255,null=True, blank=True)
	email_imap_server = models.CharField(max_length=255,null=True, blank=True)
	email_imap_port = models.CharField(max_length=255,null=True, blank=True)
	email_configured = models.BooleanField(max_length=255,null=False,blank=False, default=0)
	num_emails_queued =models.IntegerField(null=False,blank=False,default=0)
	num_new_emails = models.IntegerField(null=False,blank=False,default=0)
	last_modified=models.DateTimeField(auto_now=True)
