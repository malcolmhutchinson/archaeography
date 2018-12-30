
from django.conf.urls import url
import views

urlpatterns = [
    # The home pages
    url(r'^$', views.homepage, name='Geographic data collection'),

    url(r'^airphoto/newframe/$', views.airphoto_newframe),
    url(r'^airphoto/([/\w-]*)$', views.airphoto),
    url(r'^cadastre/([/\w-]*)$', views.cadastre),
    url(r'^lidar/([/\w-]*)$', views.lidar),
    url(r'^ortho/([/\w-]*)$', views.orthophoto),
    url(r'^topo/([/\w-]*)$', views.topomap),
    url(r'^topo/geotif/([/\.\w-]*)$', views.topomap),
]
