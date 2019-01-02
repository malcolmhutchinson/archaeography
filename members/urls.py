from django.conf.urls import url

import members.views as views
from nzaa.models import Site

urlpatterns = [
    url(r'', views.home)


]
