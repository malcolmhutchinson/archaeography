"""home URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/

Archaeography home URL configuration

There are public and private apps, or site sections. Public ones can
be seen without having a member id, and private ones require that the
user be a member of the site.

Public apps

    HOME                           /
    Bibliography of archaeology    /biblio/
    Blog                           /blog/
    NZAA archaeological sites      /archaeology/


Private apps

    Field operations               /field/
    Manuals                        /manual/
    NZAA app                       /nzaa/

"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
import views

urlpatterns = [
    # The home page
    url(r'^$', views.home, name='Archaeography home'),

    url(r'^accounts/login/', views.login_site, name='login'),
    url(r'^admin/', admin.site.urls),
    url(r'^antechamber/', views.login_site, name='login'),
    url(r'^geolib/', include('geolib.urls')),
    url(r'^logoff/', views.logoff, name='logout'),
    url(r'^manuals/([\w/-]*)', views.manuals),
    url(r'^member/', include('members.urls')),
    url(r'^nzaa/', include('nzaa.urls')),
    url(r'^favicon\.ico$',
        RedirectView.as_view(url='/static/img/favicon.ico')),
]
