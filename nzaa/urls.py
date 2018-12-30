
from django.conf.urls import url

import nzaa.views as views
from nzaa.models import Site

urlpatterns = [
    #   The home pages
    url(r'^$', views.homepage, name='NZAA application'),
    url(r'^create/$', views.site_create),
    url(r'^search/$', views.search),
    url(r'^updates/(\w*)$', views.user_updates),

    #   Sitelists.
    url(r'^sitelists/([\w/-]*)', views.sitelists),
    url(r'^sitelist/create/$', views.new_sitelist),

    #   Actors, features, periods, nzaa regions, regions, tlas.
    url(r'^actors/([\w/-]*)', views.actors),
    url(r'^actor/([\w/-]*)', views.actors),
    url(r'^changes/', views.changes),
    url(r'^features/([\w/-]*)', views.features),
    url(r'^feature/([\w/-]*)', views.features),
    url(r'^nzaareg/([\w/-]*)', views.nzaa_regions),
    url(r'^periods/([\w/-]*)', views.periods),
    url(r'^period/([\w/-]*)', views.periods),
    url(r'^regions/', views.regions),
    url(r'^tlas/([\w/-]*)', views.tlas),

    #   New site records.
    url(r'^newsites/$', views.newsites),
    url(r'^([ABC][A-Z][0-9][0-9]/\d+)/$', views.newsite),
    url(r'^([ABC][A-Z][0-9][0-9]/\d+)/(edit)/$', views.newsite),
    url(r'^newsites/([\w/-]*)$', views.newsites),
    url(r'^create/$', views.site_create),

    #   View site and individual update.
    url(r'^([A-Za-z]\d{2}/\d+)/$', views.site),
    url(r'^([A-Za-z]\d{2}/\d+-\d+)/$', views.site),
    url(r'^([A-Z]\d{2}/\d+)/update/$', views.site_update),
    url(r'^([A-Za-z]\d{2}/\d+)/(\w+)/$', views.site),

    #   Selected lists of site records.
    url(r'([A-Za-z]\d{2})/$', views.selector),
    url(r'^(\w*)/$', views.selector),
    url(r'^(\w*)/(\w+)/$', views.selector),

    #   View or edit a temporary site record.
    url(r'^([A-Z]+/\d+)/(\w+)/$', views.site),
    url(r'^([A-Z]+/\d+)/$', views.site),
    url(r'^([A-Z]+/\d+-\d+)/$', views.site),
    url(r'^([A-Z]+/\d+-\d+)/edit/$', views.update_edit),
    url(r'^([A-Z]+/\d+-\d+)/submit/$', views.update_submit),

    #   Update site, and edit updates.
    url(r'^([A-Z]\d{2}/\d+-\d+)/edit/$', views.update_edit),
    url(r'^([A-Z]\d{2}/\d+-\d+)/submit/$', views.update_submit),
]
