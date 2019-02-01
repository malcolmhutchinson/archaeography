from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, WKBWriter, GEOSGeometry

import datetime
import os

import forms
import geolib.models
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

def boundary_report(request, boundary_id):
    """Display a report of sites within a boundary."""

    context = build_context(request)
    context['jsortable'] = True
    template = 'member/boundary.html'
    context['main_form'] = MAIN_FORM
    notifications = []

    try:
        boundary = models.Boundary.objects.get(id=boundary_id)
        context['boundary'] = boundary
        context['h1'] = boundary.name  # Should change to boundary.title.
        context['editForm'] = forms.BoundaryForm(instance=boundary)
    except models.Boundary.DoesNotExist:
        context['notFound'] = True
        context['h1'] = "Boundary record not found"
        return render(request, template, context)

    if not boundary.member == request.user.member:
        context['notAuthorised'] = True
        context['h1'] = "Boundary record not authorised"
        context['boundary'] = None
        return render(request, template, context)

    if request.POST:
        editForm = forms.BoundaryForm(request.POST, instance=boundary)
        if editForm.is_valid():
            editForm.save()
            notifications.append('Saving boundary record.')
            context['editForm'] = editForm
            context['h1'] = boundary.name  # Should change to boundary.title.
        
    context['notifications'] = notifications
    context['title'] = context['h1'] + " | " + context['title']
    
    return render(request, template, context)


def boundaries(request, command):
    """List the member's boundary files."""

    context = build_context(request)
    template = 'member/boundaries.html'
    context['h1'] = "List of your boundary files, "
    context['h1'] += request.user.username
    context['title'] = context['h1'] + " | archaeography.nz"
    context['jsortable'] = True

    # Read the KML files in the boundary directory.
    dirpath = os.path.join(
        settings.STATICFILES_DIRS[0],
        'member', request.user.username, 'boundary',
    )
    geom_files = []
    if not os.path.isdir(dirpath):
        geom_files = None
    else:
        allfiles = os.listdir(dirpath)
        for f in allfiles:
            base, ext = os.path.splitext(f)
            if ext in BOUNDARY_EXT:
                geom_files.append(f)
    context['geom_files'] = geom_files

    # Get the member's boundary records from the db.
    context['records'] = models.Boundary.objects.filter(
        member=request.user.member)

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
        context['boundaryFileForm'] = forms.BoundaryFileForm(request.POST)
        boundary = context['boundaryFileForm'].save(commit=False)
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

        context['notifications'].append("File " + fname + " submitted.")
        
        try:
            ds = DataSource(pathname)
            geoms = ds[0].get_geoms()

            # extract polygons from the geometry.
        except:
            context['notifications'].append(
                "This is not an OGR file. File not uploaded.")
            os.remove(pathname)
            return render(request, template, context)

        polys = []
        for g in geoms:
            if 'Polygon' in g.geom_type.name:
                polys.append(g)

        if len(polys) < 1:
            note = "No polygons in the file. "
            note += "We can't use this as a boundary, and the "
            note += "file has not been uploaded."
            context['notifications'].append(note)
            os.remove(pathname)
            return render(request, template, context)

        if len(polys) > 1:
            note ="Multiple polygon geometries found. Only the first "
            note += "will be used."
            context['notifications'].append(note)

        # If we get to here, we've got a polygon (or more than one),
        # and we can try loading it into the model object.
        wkb = WKBWriter()
        tmp = wkb.write(MultiPolygon(polys[0].geos))
        
        boundary.geom = GEOSGeometry(tmp, srid=4326).transform(2193, clone=True)
        boundary.member = request.user.member
        boundary.fname = fname
        boundary.save()
        context['notifications'].append('KML file uploaded successfully.')
                
    return render(request, template, context)


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
    context['newsites'] = nzaa.models.NewSite.objects.filter(
        owner=request.user.username)
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
