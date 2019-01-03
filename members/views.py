from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.contrib.gis.gdal import DataSource

import os

import forms
import home.views
import models
import nzaa.models
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

def boundaries(request, command):
    """List the member's boundary files."""

    context = build_context(request)
    template = 'member/boundaries.html'
    context['h1'] = "List of your boundary files, "
    context['h1'] += request.user.username
    context['title'] = context['h1'] + " | archaeography.nz"
    context['jsortable'] = True

    return render(request, template, context)


def upload_boundary(request):
    """Form and handling for uploading KML boundary files."""
    
    context = build_context(request)
    template = 'member/uploadboundary.html'
    context['h1'] = "Upload a new boundary file"
    context['title'] = context['h1'] + " | archaeography.nz"
    context['jsortable'] = True
    context['main_form'] = MAIN_FORM
    context['boundaryFileForm'] = forms.BoundaryFileForm()
    context['uploadFile'] = forms.UploadFile()
    context['notifications'] = []

    if request.POST:
        boundaryFileForm = forms.BoundaryFileForm(request.POST)
        boundary = boundaryFileForm.save(commit=False)
        fname = str(request.FILES['filename']).replace(' ', '_')
        base, ext = os.path.splitext(fname)
        if ext not in BOUNDARY_EXT:
            context['notifications'].append(
                "Not a KML file. File not processed, try another file.")
            context['boundaryFileForm'] = boundaryFileForm 
            return render(request, template, context)

        filepath = os.path.join(
            settings.STATICFILES_DIRS[0],
            'member/', request.user.username, 'boundary')

        request.user.member.mkdir()
        if not os.path.isdir(filepath):
            os.mkdir(filepath)

        pathname = os.path.join(filepath, fname)

        f = request.FILES['filename']
        with open(pathname, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        boundary.fname = fname
        ds = DataSource(filepath)
        layer = ds[0]

        mapping = {'geom': 'POLYGON',}

        context['notifications'].append('KML file uploaded successfully')
                
    return render(request, template, context)



# Copied from home.views. Needs rewriting.
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

    context['lists'] = nzaa.models.SiteList.objects.filter(
        owner=request.user.username)
    context['updates'] = nzaa.models.Update.objects.filter(
        owner=request.user.username)

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
