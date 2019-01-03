from django.conf.urls import url
import members.views as views
from nzaa.models import Site

urlpatterns = [
    #   The home pages

    url(r'^upload/boundary/$', views.upload_boundary),
    url(r'^([\w-]*)/boundaries/$', views.boundaries),
    url(r'^([\w-]*)/$', views.homepage),

]
