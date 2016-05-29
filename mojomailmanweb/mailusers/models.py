from __future__ import unicode_literals

from django.db import models

# Create your models here.

class MojoMailManUser(models.Model):
	username = models.CharField(max_length=200, unique=True)
	password = models.CharField(max_length=256)
	homedir = models.CharField(max_length=256)
	email1 = models.CharField(max_length=256,null=True, blank=True)
	email1_smtp_server = models.CharField(max_length=256,null=True, blank=True)
	email1_smtp_port = models.CharField(max_length=256,null=True, blank=True)
	email1_imap_server = models.CharField(max_length=256,null=True, blank=True)
	email1_imap_port = models.CharField(max_length=256,null=True, blank=True)
	
	email2 = models.CharField(max_length=256,null=True, blank=True)
	email2_smtp_server = models.CharField(max_length=256,null=True, blank=True)
	email2_smtp_port = models.CharField(max_length=256,null=True, blank=True)
	email2_imap_server = models.CharField(max_length=256,null=True, blank=True)
	email2_imap_port = models.CharField(max_length=256,null=True, blank=True)

	email3 = models.CharField(max_length=256,null=True, blank=True)
	email3_smtp_server = models.CharField(max_length=256,null=True, blank=True)
	email3_smtp_port = models.CharField(max_length=256,null=True, blank=True)
	email3_imap_server = models.CharField(max_length=256,null=True, blank=True)
	email3_imap_port = models.CharField(max_length=256,null=True, blank=True)
