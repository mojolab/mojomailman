from django.contrib import admin
from .models import EmailAddress


class EmailAdmin(admin.ModelAdmin):
	list_display = ('email','user')

admin.site.register(EmailAddress,EmailAdmin)
	
# Register your models here.
