from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, WKBWriter, GEOSGeometry

import datetime
import os

import authority
import forms
import geolib.models
import home.views
import models
import nzaa.models as nzaa
import settings

MAIN_FORM = {
    'id': 'members',
    'action': '',
    'method': 'POST',
    'class': 'mainForm',
}

BOUNDARY_EXT = (
    '.kml', '.KML',
)

@login_required
def homepage(request, command=None):
    """Display updates and sitelists belonging to the authenticated user. """

    context = build_context(request)
    context['h1'] = "This is your archaeography home page, "
    context['h1'] += request.user.username
    context['title'] = context['h1'] + " | archaeography.nz"
    context['jsortable'] = True

    try:
        models.Member.objects.get(user=request.user)
        context['memberForm'] = forms.MemberForm(instance=request.user.member)
        template = 'member.html'
    except models.Member.DoesNotExist:
        template = 'home/user.html'
        context['h1'] = "User page for " + request.user.username
        return render(request, template, context)

    context['memberForm'] = forms.MemberForm(instance=request.user.member)

    if authority.nzaa_member(request.user):
        context['lists'] = nzaa.SiteList.objects.filter(
            owner=request.user.username)
        context['updates'] = nzaa.Update.objects.filter(
            owner=request.user.username)
        context['newsites'] = nzaa.NewSite.objects.filter(
            owner=request.user.username)
    if authority.boundaries(request):
        context['boundaries'] = models.Boundary.objects.filter(
            member=request.user.member)

    if request.POST:
        memberForm = forms.MemberForm(
            request.POST, instance=request.user.member
        )
        if memberForm.is_valid():
            memberForm.save()
            context['memberForm'] = memberForm

    return render(request, template, context)


def build_context(request):
    context = home.views.build_context(request)

    return context
