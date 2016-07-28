from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^emailaddress/([0-9]+)/generate_config_files', views.test)
]
