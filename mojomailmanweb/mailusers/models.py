from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser,User

# Create your models here.

class EmailAddress(models.Model):
	user = models.ForeignKey(User)
	email = models.CharField(max_length=255,null=True, blank=True,unique=True)
	email_smtp_server = models.CharField(max_length=255,null=True, blank=True)
	email_smtp_port = models.CharField(max_length=255,null=True, blank=True)
	email_imap_server = models.CharField(max_length=255,null=True, blank=True)
	email_imap_port = models.CharField(max_length=255,null=True, blank=True)
