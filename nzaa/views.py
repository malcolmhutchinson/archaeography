"""View functions for the NZAA application


Infrastructure

    Breadcrumbs

    These are links going back the way you came. They are compiled in
    the non-view method

            context['breadcrumbs'] = build_breadcrumbs(request)



Session variables - site record lists


    The session variable is used to store lists of site identifiers,
    such that a list of records can be stepped through, via links in
    the breadcrumbs.

    Any such list of site records intended to be stepped through in
    this manner is called a siteset. It is

    request.session['siteset'] should be set with this dictionary structure:

        siteset = {
            'setname': "(eg) Recent changes",
            'seturl': os.path.join(settings.BASE_URL, URL),
            'setlist': setlist,
        }

        request.session['siteset'] = siteset

    Where setlist is a list of NZAA identifiers.

    Set the siteset before calling build_breadcrumbs()

"""
import datetime
import os
import locale
import markdown2 as markdown

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.gis.geos import Point
from django.core.serializers import serialize

from django.db import IntegrityError

from django.db.models import F
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.db.models import F
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, WKBWriter, GEOSGeometry


from django.db import transaction

from geolib.models import Region, TerritorialAuthority, NZMSgrid, Topo50grid
import analyse
import authority
import forms
import home.views
import models
import scrape
import settings

import utils

MAIN_FORM = {
    'id': 'siteRecord',
    'action': '',
    'method': 'POST',
    'class': 'mainForm',
}

BOUNDARY_EXT = (
    '.kml', '.KML',
)

# Limit of site records to list in one whack.
LIMIT = 100


@user_passes_test(authority.nzaa_member)
def actors(request, command=None):

    URL = 'actors/'
    template = 'nzaa/Actors.html'
    context = build_context(request)
    context['commands'] = authority.commands(request)
    context['jsortable'] = True
    context['simpleSearch'] = forms.SimpleSearch

    setlist = None
    siteset = None

    if command:
        try:
            a = models.Actor.objects.get(id=command)
            setlist = list(a.sites.all().values_list('nzaa_id', flat=True))
            siteset = {
                'setname': a.sourcename,
                'seturl': os.path.join(settings.BASE_URL, URL, command),
                'setlist': setlist,
            }
            request.session['siteset'] = siteset

            identifiers = ""
            for i in setlist:
                identifiers += "'" + i + "', "
            identifiers = identifiers[:-2]
            context['identifiers'] = identifiers

        except models.Actor.DoesNotExist:
            a = None

        context['actor'] = a

        request.session['siteset'] = siteset
        context['breadcrumbs'] = build_breadcrumbs(request)
        return render(request, template, context)

    request.session['siteset'] = siteset
    context['actors'] = models.Actor.objects.all()
    context['breadcrumbs'] = build_breadcrumbs(request)
    return render(request, template, context)


def boundaries(request):
    """List the member's boundary files."""

    context = build_context(request)
    context['commands'] = authority.boundary_commands(request)
    context['nav'] = 'nzaa/nav_boundary.html'
    context['h1'] = "List of your boundary reports, "
    context['h1'] += request.user.username
    context['title'] = context['h1'] + " | archaeography.nz"
    context['jsortable'] = True

    template = 'nzaa/Boundaries.html'

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
        owner=request.user)

    return render(request, template, context)


def boundary_report(request, boundary_id):
    """Display a report of sites within a boundary."""

    context = build_context(request)
    context['commands'] = authority.boundary_commands(request)
    context['nav'] = 'nzaa/nav_boundary.html'
    context['jsortable'] = True
    context['main_form'] = MAIN_FORM
    notifications = []

    template = 'nzaa/boundary.html'

    try:
        boundary = models.Boundary.objects.get(id=boundary_id)
        context['boundary'] = boundary
        context['h1'] = boundary.title
        context['editForm'] = forms.BoundaryForm(instance=boundary)
    except models.Boundary.DoesNotExist:
        context['notFound'] = True
        context['h1'] = "Boundary record not found"
        return render(request, template, context)

    if not boundary.owner == request.user:
        context['notAuthorised'] = True
        context['h1'] = "Boundary record not authorised"
        context['boundary'] = None
        return render(request, template, context)

    if boundary.parcels_intersecting().count() < 50:
        context['cadastral_report'] = True

    if request.POST:
        editForm = forms.BoundaryForm(request.POST, instance=boundary)
        if editForm.is_valid():
            editForm.save()
            notifications.append('Saving boundary record.')
            context['editForm'] = editForm
            context['h1'] = boundary.title

    analysis = analyse.Site(boundary.sites_identified())
    context['sites_by_lgcy_type'] = analysis.count_by_lgcy_type()

    context['editable'] = boundary.is_editable(request)
    context['viewable'] = boundary.is_viewable(request)
    context['notifications'] = notifications
    context['title'] = context['h1'] + " | " + context['title']
    
    return render(request, template, context)


def boundary_upload(request):
    """Form and handling for uploading KML boundary files."""
    
    context = build_context(request)
    context['commands'] = authority.boundary_commands(request)
    context['nav'] = 'nzaa/nav_boundary.html'
    context['h1'] = "Upload a new boundary file"
    context['title'] = context['h1'] + " | archaeography.nz"
    context['jsortable'] = True
    context['main_form'] = MAIN_FORM
    context['boundaryForm'] = forms.BoundaryForm()
    context['uploadFile'] = forms.UploadFileRequired()
    context['notifications'] = []

    template = 'nzaa/uploadboundary.html'

    if request.POST:
        context['boundaryForm'] = forms.BoundaryForm(request.POST)
        boundary = context['boundaryForm'].save(commit=False)
        fname = str(request.FILES['filename']).replace(' ', '_')
        boundary.fname = fname
        base, ext = os.path.splitext(fname)

        # Check that it's a KML file by looking at the extension.
        if ext not in BOUNDARY_EXT:
            context['notifications'].append(
                "Not a KML file. File not processed, try another file.")

            return render(request, template, context)

        # We have to save the file before we can analyse it.
        filepath = boundary.filepath()

        if not os.path.isdir(filepath):
            print "Making directory at ", filepath
            os.makedirs(filepath)

        pathname = os.path.join(filepath, fname)

        f = request.FILES['filename']
        with open(pathname, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        context['notifications'].append("File " + fname + " submitted.")

        try:
            ds = DataSource(pathname)
            geoms = ds[0].get_geoms()

        except:
            context['notifications'].append(
                "This is not an OGR file. File not uploaded.")
            os.remove(pathname)
            os.rmdir(filepath)
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
            so.rmdir(filepath)
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
        boundary.owner = request.user
        boundary.save()
        context['notifications'].append('KML file uploaded successfully.')
                
    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def changes(request):
    """List records changed since last scraping."""

    URL = 'changes/'
    idlist = ''
    sites = None
    template = 'nzaa/Changes.html'
    context = build_context(request)
    context['commands'] = authority.commands(request)
    context['jsortable'] = True
    context['simpleSearch'] = forms.SimpleSearch

    transaction.set_autocommit(True)

    tunit = 'day'
    query = 'SELECT "nzaa_id" '
    query += "FROM nzaa_site WHERE "
    query += "date_trunc('" + tunit + "', last_change) = "
    query += "date_trunc('" + tunit + "', extracted) "
    query += "ORDER BY nzms_sheet, ordinal "

    sites = models.Site.objects.raw(query)
    sites_list = list(sites)

    context['count'] = len(sites_list)

    setlist = []
    for site in sites:
        setlist.append(site.nzaa_id)
        idlist += "'" + site.nzaa_id + "', "

    # Causes a problem if there are no site records.
    context['last_scan'] = models.Site.objects.all().order_by(
        '-extracted')[0].extracted

    title = "Changed site records since "
    title += context['last_scan'].strftime('%Y-%m-%d')
    title += " | " + context['title']
    context['title'] = title

    context['sites'] = sites
    context['idlist'] = idlist[:-2]

    siteset = {
        'setname': "Recent changes",
        'seturl': os.path.join(settings.BASE_URL, URL),
        'setlist': setlist,
    }
    request.session['siteset'] = siteset
    context['breadcrumbs'] = build_breadcrumbs(request)
    return render(request, template, context)

@user_passes_test(authority.nzaa_member)
def document(request, doc_id):
    URL = 'document/'
    template = 'nzaa/Document.html'
    context = build_context(request)
    context['commands'] = authority.commands(request)
    context['h1'] = 'Document ' + doc_id
    context['doc_id'] = doc_id

    try:
        document = models.Document.objects.get(id=doc_id)
        context['h1'] = document.title
        context['document'] = document
        context['site'] = document.update.site
        context['valid_updates'] = document.update.site.updates_all()

    except models.Document.DoesNotExist:
        context['h1'] = 'No record for document id ' + doc_id
        return render(request, template, context)

    if request.POST:
        form = forms.DocumentForm(request.POST, instance=document)
        if form.is_valid():
            doc = form.save(commit=False)
            
            if request.POST['update']:
                try:
                    u = models.Update.objects.get(
                        update_id=request.POST['update'])
                    doc.update = u
                except models.Update.DoesNotExist:
                    pass

            doc.save()

    context['documentForm'] = forms.DocumentForm(instance=document)

    return render(request, template, context)

@user_passes_test(authority.nzaa_member)
def features(request, command=None):

    URL = 'features/'
    template = 'nzaa/Features.html'
    context = build_context(request)
    context['commands'] = authority.commands(request)
    context['jsortable'] = True
    context['simpleSearch'] = forms.SimpleSearch

    setlist = None
    siteset = None

    if command:
        try:
            f = models.Feature.objects.get(id=command)
            setlist = list(f.sites.all().values_list('nzaa_id', flat=True))
            siteset = {
                'setname': f.name,
                'seturl': os.path.join(settings.BASE_URL, URL, command),
                'setlist': setlist,
            }

            identifiers = ""
            for i in setlist:
                identifiers += "'" + i + "', "
            identifiers = identifiers[:-2]
            context['identifiers'] = identifiers

        except models.Feature.DoesNotExist:
            f = None

        context['feature'] = f

        request.session['siteset'] = siteset
        context['breadcrumbs'] = build_breadcrumbs(request)
        return render(request, template, context)

    request.session['siteset'] = siteset
    #print "SITESET", siteset
    context['features'] = models.Feature.objects.all()
    context['breadcrumbs'] = build_breadcrumbs(request)
    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def homepage(request):

    context = build_context(request)
    context['h1'] = 'NZAA archaeological site records'
    context['title'] = context['h1'] + " | archaeography.nz"
    context['subhead'] = 'Modelling the Site Recording Scheme (SRS)'
    context['jsortable'] = True
    context['total_records'] = models.Site.objects.all().count()
    context['total_documents'] = models.Document.objects.all().count()
    
    context['user_groups'] = authority.group_memberships(request)
    request.session['siteset'] = None

    template = 'nzaa.html'

    #   Natural groups of sites.
    context['nzaa_region'] = []
    for item in sorted(settings.NZAA_REGION.keys()):
        context['nzaa_region'].append((item, settings.NZAA_REGION[item][0]))

    context['region'] = []
    for item in sorted(settings.REGION.keys()):
        context['region'].append((item, settings.REGION[item][0]))

    context['tla'] = []
    for item in sorted(settings.TLA.keys()):
        context['tla'].append((item, settings.TLA[item][0]))

    context['nzms260'] = []
    for item in settings.NZMS260:
        context['nzms260'].append((item, item))

#   User's lists, new sites and updates.
    context['updates'] = models.Update.objects.filter(
        owner=request.user.username)
    context['sitelists'] = models.SiteList.objects.filter(
        owner=request.user.username)
    context['newsites'] = models.NewSite.objects.filter(
        owner=request.user.username)

#   Site attribute lists.
    context['actors'] = models.Actor.objects.all()
    context['features'] = models.Feature.objects.all()
    context['periods'] = models.Periods.objects.all()

    context['commands'] = authority.commands(request)
    context['breadcrumbs'] = build_breadcrumbs(request)

    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def new_sitelist(request):
    """Create a sitelist record.
    """

    template = 'nzaa/CreateSiteList.html'
    warnings = None
    request.session['siteset'] = None

    context = build_context(request)
    context['buttons'] = ('create',)
    context['commands'] = authority.commands(request)
    context['main_form'] = MAIN_FORM

    context['CreateSiteListForm'] = forms.SiteList()

    if request.GET:
        if 'addsites' in request.GET:
            context['addsites'] = request.GET['addsites']

    if request.POST:
        createForm = forms.SiteList(request.POST)
        if createForm.is_valid():
            sl = createForm.save(commit=False)
            sl.owner = request.user.username
            sl.created_by = request.user.username
            sl.save()
            if request.POST['addsites']:
                sites, warnings = string2sites(request.POST['addsites'])
                for site in sites:
                    sl.sites.add(site)
            return redirect('/nzaa/sitelists/' + str(sl.id))
        context['CreateSiteListForm'] = createForm

    context['title'] = "Create a site list | " + context['title']
    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def newsite(request, site_id, command=None):
    """Display or edit a new site record.

    """
    site = None
    template = 'nzaa/NewSite.html'
    context = build_context(request)
    context['subhead'] = "New site record"
    context['title'] = "Create a new site record | archaeography.nz"
    request.session['siteset'] = None

    try:
        site = models.NewSite.objects.get(newsite_id=site_id)
        context['h1'] = site.title
    except models.NewSite.DoesNotExist:
        context['h1'] = "No record for " + site_id
        return render(request, template, context)

    if command == 'edit':
        template = 'nzaa/NewSiteEdit.html'
        context['main_form'] = MAIN_FORM
        context['buttons'] = ['save', ]
        context['subhead'] = 'Edit this new site record'
        context['NewSiteForm'] = forms.NewSiteForm(instance=site)
        context['UploadFile'] = forms.UploadFileRequired()

    if request.POST:
        NewSiteForm = forms.NewSiteForm(request.POST, instance=site)
        if NewSiteForm.is_valid():
            record = NewSiteForm.save(commit=False)

            log = [
                request.META['REMOTE_ADDR'],
                request.user.username,
                'Saving changes from newsite form.'
            ]
            record.save(log=log)

            context['NewSiteForm'] = forms.NewSiteForm(instance=record)

            if len(request.FILES) > 0:
                filename = str(request.FILES['filename']).replace(' ', '_')
                filepath = os.path.join(site.filespace_path(), filename)

                with open(filepath, 'wb+') as destination:
                    for chunk in request.FILES['filename'].chunks():
                        destination.write(chunk)

    context['commands'] = authority.commands(request, newsite=site)
    context['site'] = site

    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def newsites(request, command=None):
    """List new site rcords. Those which have not been accessioned.

    """

    template = 'nzaa/NewSites.html'
    request.session['siteset'] = None

    context = build_context(request)
    context['jsortable'] = True
    context['commands'] = authority.commands(request)
    context['allrecords'] = models.NewSite.objects.all()
    context['userrecords'] = models.NewSite.objects.filter(
        owner=request.user.username)

    context['breadcrumbs'] = build_breadcrumbs(request)
    context['title'] = "List new site records | archaeography.nz"
    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def nzaa_regions(request, command=None):
    """Compute a list of NZAA regions and the number of recorded sites.
    """

    URL = 'nzaareg/'
    template = 'nzaa/NZAAregions.html'
    context = build_context(request)

    context['commands'] = authority.commands(request)
    context['jsortable'] = True
    context['simpleSearch'] = forms.SimpleSearch

    setlist = None
    siteset = None

    nzaaregions = []
    for reg in sorted(settings.NZAA_REGION.keys()):
        sheets = settings.NZAA_REGION_SHEETS[reg]
        count = models.Site.objects.filter(nzms_sheet__in=sheets).count()
        line = (reg, reg.replace('file', ' file'), count)
        nzaaregions.append(line)

    request.session['siteset'] = siteset
    context['nzaaregions'] = nzaaregions
    context['breadcrumbs'] = build_breadcrumbs(request)
    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def periods(request, command=None):

    URL = 'periods'
    template = 'nzaa/Periods.html'
    context = build_context(request)
    context['commands'] = authority.commands(request)
    context['jsortable'] = True
    context['simpleSearch'] = forms.SimpleSearch

    setlist = None
    siteset = None

    if command:
        try:
            p = models.Periods.objects.get(id=command)
            setlist = list(p.sites.all().values_list('nzaa_id', flat=True))
            siteset = {
                'setname': p.name,
                'seturl': os.path.join(settings.BASE_URL, URL, command),
                'setlist': setlist,
            }
            request.session['siteset'] = siteset
            
            identifiers = ""
            for i in setlist:
                identifiers += "'" + i + "', "
            identifiers = identifiers[:-2]
            context['identifiers'] = identifiers

        except models.Periods.DoesNotExist:
            p = None
            request.session['siteset'] = siteset

        context['period'] = p

        request.session['siteset'] = siteset
        context['breadcrumbs'] = build_breadcrumbs(request)
        return render(request, template, context)

    request.session['siteset'] = siteset
    context['periods'] = models.Periods.objects.all()
    context['breadcrumbs'] = build_breadcrumbs(request)
    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def regions(request):

    template = 'nzaa/Regions.html'
    context = build_context(request)
    context['commands'] = authority.commands(request)
    context['jsortable'] = True
    context['simpleSearch'] = forms.SimpleSearch

    context['regions'] = Region.objects.all().order_by('id')

    context['breadcrumbs'] = build_breadcrumbs(request)
    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def search(request):
    """Search the site records.

    We get here in one of two ways: from the simple search form,
    containing a string `terms`, or by linking to the url at
    `/nzaa/search`.

    If we have terms, this string will be processed to look for
    targets in this order:

    1.  Does it fit the format for a site record identifier?

        2. Does the first letter start with 'N' or 'S'?

           Look in the `nzms_id` field, as well as the nzaa_id field.

    2.  Is it in the NZMS260 list from settings?

    3.  Is it in the regions list?

    4.  Is it in the TLA list?

    Search will redirect to addresses like single records, or natural
    groups.

    """

    URL = 'search/'
    context = build_context(request)
    site = None
    sheet = None
    ordinal = None
    terms = None

    context['TLA'] = settings.link_dictionary(settings.TLA)
    context['REGION'] = settings.link_dictionary(settings.REGION)
    context['NZMS260'] = settings.NZMS260
    context['NZAA_REGION'] = sorted(settings.NZAA_REGION.keys())

    context['commands'] = authority.commands(request)
    context['filekeeper_commands'] = authority.filekeeper_commands(request)
    context['SearchForm'] = forms.Search()
    context['simpleSearch'] = forms.SimpleSearch

    siteset = {
        'setname': None,
        'seturl': os.path.join(settings.BASE_URL, URL),
        'setlist': [],
    }

    if request.GET:
        if request.GET['terms']:
            terms = request.GET['terms']

#   Begin testing the terms with:
#   does it fit the form of an NZAA identifier?
    parts = terms.split('/')
    site_ids = []
    if len(parts) == 2:
        sheet = parts[0].upper()
        try:
            ordinal = int(parts[1])
        except ValueError:
            pass

        if sheet and ordinal:

            if sheet[0] == 'N' or sheet[0] == 'S':
                nzms_id = sheet + '/' + str(ordinal)
                try:
                    site = models.Site.objects.get(nzms_id=nzms_id)
                    site_ids.append(site.nzaa_id)
                except models.Site.DoesNotExist:
                    pass

            nzaa_id = sheet + '/' + str(ordinal)
            site_ids.append(nzaa_id)

            if len(site_ids) == 1:
                return redirect(os.path.join(settings.BASE_URL, nzaa_id))
            else:
                context['sites'] = models.Site.objects.filter(
                    nzaa_id__in=site_ids)
                context['terms'] = terms
                siteset['setlist'] = site_ids
                siteset['setname'] = 'search ' + terms
                siteset['seturl'] += '?terms=' + terms
                request.session['siteset'] = siteset
                context['breadcrumbs'] = build_breadcrumbs(request)

                return render(request, 'nzaa/Search.html', context)

#   Next test: is it in the NZMS260 list?
    if terms.upper() in settings.NZMS260:
        return redirect(os.path.join(settings.BASE_URL, terms.upper()))

#   Is it in the NZAA file districts?
    if terms in settings.NZAA_REGION.keys():
        return redirect(os.path.join(settings.BASE_URL, terms))

#   Is it in the regions?
    if terms in settings.REGION.keys():
        return redirect(os.path.join(settings.BASE_URL, terms))

#   Is it in the territorial authorities?
    if terms in settings.TLA.keys():
        return redirect(os.path.join(settings.BASE_URL, terms))

    return redirect(settings.BASE_URL)


@user_passes_test(authority.nzaa_member)
def selector(request, command, option=None):
    """The main site list display view.

    This view interprets URL directions and GET values to select
    subsets from the site record collection. Natural groups, such as
    "all the sites in Hamilton City", or "all the sites in the Waikato
    site file" are supported by extensions to the nzaa url:

        /nzaa/hamlton/
        /nzaa/waikatofile/

    You can also add certain GET variables, to refine the search. All
    the pa in Hamilton can be reached by typing:

        /nzaa/hamilton/?site_type=pa

    Of those pa records, which ones are sparse?

        /nzaa/hamilton/?site_type=pa&quality=sparse
    """

    context = build_context(request)
    request.session['siteset'] = None
    listtype = None
    sites = None
    template = 'nzaa/SitesList.html'
    h1 = "Sorry, I don't know what you are asking for."
    first = None
    last = None
    nfirst = None
    nlast = None
    context['first'] = None
    context['last'] = None

    siteset = {
        'setname': None,
        'seturl': os.path.join(settings.BASE_URL, command),
        'setlist': [],
    }

    context['NZMS260'] = settings.NZMS260
    context['TLA'] = settings.link_dictionary(settings.TLA)
    context['REGION'] = settings.link_dictionary(settings.REGION)
    context['NZAA_REGION'] = settings.link_dictionary(settings.NZAA_REGION)
    context['jsortable'] = True
    context['simpleSearch'] = forms.SimpleSearch

    if option == "assess":
        template = 'nzaa/SitesListAssessment.html'

    context['mapimage'] = (
        os.path.join(settings.STATIC_URL, 'img', command + '.png'),
        'Map of ' + command
    )

    if command in settings.TLA.keys():
        tla = settings.TLA[command][0]
        h1 = tla
        sites = models.Site.objects.filter(tla=tla)
        listtype = 'tla'
        siteset['setname'] = tla

    elif command in settings.REGION.keys():
        region = settings.REGION[command][0]
        h1 = region
        sites = models.Site.objects.filter(region=region)
        listtype = 'region'
        siteset['setname'] = region

    elif command in settings.NZAA_REGION.keys():
        region = settings.NZAA_REGION[command][0]
        h1 = region
        sheets = settings.NZAA_REGION_SHEETS[command]
        sites = models.Site.objects.filter(nzms_sheet__in=sheets)
        context['sheets'] = sheets
        listtype = 'nzaa'
        siteset['setname'] = region

    elif command.upper() in settings.NZMS260:
        command = command.upper()
        h1 = command + " NZMS260 sheet"
        context['sheet'] = command
        sites = models.Site.objects.filter(nzms_sheet=command)
        listtype = 'nzms_sheet'
        siteset['setname'] = h1

    if sites:
        analysis = analyse.Site(sites)
        context['sites_by_lgcy_type'] = analysis.count_by_lgcy_type()

#   Find unfilled ordinals in a NZMS260 sheet.
    if listtype == "nzms_sheet":
        missing = ""
        count = 0
        ordinals = list(sites.values_list('ordinal', flat=True))
        for n in range(1, sites[len(sites)-1].ordinal + 1):
            if n not in ordinals:
                count += 1
                missing += command + "/" + str(n) + ", "
        missing = missing[:-2]
        context['missing_records'] = missing
        context['count_missing'] = count

#   Create a new site list object from checked records (depreciated).
    if request.POST:
        if request.POST['command'] == 'new from selected':
            selected = ""
            for i in request.POST.keys():
                if utils.is_siteid(i):
                    selected += i + ","
            return redirect('/nzaa/sitelist/create?addsites=' + selected)

#   Provide for short versions of the full set of site records (so
#   they can be displayed eg. 100 at a time).
    if request.GET:
        if 'first' in request.GET.keys() or 'last' in request.GET.keys():
            if request.GET['first'] == 'all' or request.GET['last'] == 'all':
                sites = sites
            else:
                try:
                    first = int(request.GET['first'])
                    last = int(request.GET['last'])
                    if first > last:
                        tmp = last
                        last = first
                        first = tmp

                    if last > sites.count():
                        last = sites.count()
                    nfirst = last
                    nlast = nfirst + LIMIT
                    if nlast > sites.count():
                        nlast = sites.count()

                except ValueError:
                    pass
                sites = sites[first:last]

        (group_name, sites) = analyse.site_subselect(request, sites)
        context['group_name'] = group_name

    if sites:
        context['sitecount'] = sites.count()
        siteset['setlist'] = list(sites.values_list('nzaa_id', flat=True))

    context['h1'] = h1
    context['title'] = "Site records for " + h1 + " | archaeography.nz"
    context['listname'] = h1
    context['sites'] = sites
    context['commands'] = authority.commands(request)

    request.session['siteset'] = siteset
    context['breadcrumbs'] = build_breadcrumbs(request)
    context['first'] = first
    context['last'] = last
    context['nfirst'] = nfirst
    context['nlast'] = nlast

    return render(request, template, context)


def site(request, command, argument=None):
    """Display an archaeological site record.

    command:      Usually an NZAA identifier or an update identifier.

    argument:     To modify the command, for example, to review the
                  site record.

    Quite a complex view. It does these things in order, after
    initialisation:

    1.  Determines the nzaa_id and update_id from command.

    2.  Build a context variable from a function at the end of
        this module.

    3.  Retreive the site record. If this fails, throw an error and
        redisplay the page.

    4.  Test the GET condition, and set alternative display
        templates.

    5.  If a single update is requested, make that the only update record.

    6.  Test arguments available to non-filekeepers.

    7.  Set the flekeeper additional features.

        1.  Filekeeper commands
        2.  Site review.

    8.  Deal with the POST.

        1.  Site review.

    9.  Return the response object.

    """


    site = None
    update = None
    siteReviewForm = None
    siteAssessForm = None
    nzaa_id = None
    update_id = None
    template = 'nzaa/Site.html'

    context = build_context(request)

#   Find the nzaa_id, sheet identifier and ordinal.
    split = command.split('-')
    nzaa_id = split[0]
    (sheet, ordinal) = nzaa_id.split("/")
    ordinal = int(ordinal)

    if len(split) > 1:
        update_id = command

    context['nzaa_id'] = nzaa_id
    context['update_id'] = update_id

#   If the user is not authenticated, change the template and return.
    if not request.user.is_authenticated:
        template = 'nzaa/SiteNotAuth.html'
        context['h1'] = "NZAA archaeological site record " + nzaa_id
        return render(request, template, context)
    
#   Go download the record from ArchSite.
    if argument == "scrape":
        s = scrape.Scrape([nzaa_id])

    context['breadcrumbs'] = build_breadcrumbs(request)
    context['simpleSearch'] = forms.SimpleSearch

#   Find the site record, and deal with not finding it.
    try:
        site = models.Site.objects.get(nzaa_id=nzaa_id)
        context['site'] = site
        context['map'] = analyse.MapSite(site)

    except models.Site.DoesNotExist:

        error = "We're sorry, there is no record for "
        error += command + " in our system."
        context['notifications'].append(error)
        context['site_id'] = command
        context['archsite'] = settings.SITE_PAGE + command
        context['commands'] = authority.commands(request)
        context['h1'] = "No record for " + nzaa_id

        if context['filekeeper']:
            context['filekeeper_commands'] = authority.filekeeper_commands(
                request)

        return render(request, template, context)

    # Depreciated.
    if argument == 'mapfile':
        context['map'] = site.mapfile()
        template = 'nzaa/mapfile_site.map'
        return render(request, template, context)

    if update_id:
        try:
            context['update'] = models.Update.objects.get(update_id=update_id)
        except models.Update.DoesNotExist:
            context['update'] = None

    if not authority.nzaa_member(request.user):
        template = 'nzaa/Site-public.html'
        context['site'] = site
        context['authorised'] = False
        context['h1'] = site.nzaa_id + " | NZAA archaeological site record"
        context['title'] = context['h1'] + " | archaeography.nz"
        context['subhead'] = "from the NZ Archaeological Association's "
        context['subhead'] += "Site Recording Scheme (SRS)"
        return render(request, template, context)

    context['jsortable'] = True

    if request.GET:
        # Permits different templates to be used, with "?view=templatename"
        if request.GET['view']:
            template = "nzaa/siteview/" + request.GET['view']

    if update_id:
        try:
            update = models.Update.objects.get(update_id=update_id)
            site.set_update(update_id)
            context['buttons'] = update.buttons(request.user)
        except models.Update.DoesNotExist:
            error = "No update by that identifier. Here is the whole record"
            context['notifications'].append(error)

    if argument == 'review':
        context['review'] = True
        context['buttons'] = ('save', )
        update_id = None
        r = models.SiteReview()
        siteReviewForm = forms.SiteReview(instance=site)

    elif argument == 'normalise':
        context['command'] = 'setup'
        template = 'nzaa/SiteNormalise.html'
        a = analyse.Normalise(site)
        context['suggested_dates'] = a.find_dates()
        context['suggested_updates'] = a.find_updates()

        context['valid_updates'] = site.updates_all()

    if context['filekeeper']:
        context['filekeeper_commands'] = authority.filekeeper_commands(
            request, site=site)

    if context['buttons']:
        context['main_form'] = MAIN_FORM

    if request.POST:

        if argument == 'review':
            log = (
                request.META['REMOTE_ADDR'],
                request.user.username,
                "Changes after review.",
            )

            old_values = site.old_values()

            siteReviewForm = forms.SiteReview(request.POST, instance=site)
            if siteReviewForm.is_valid():

                old_values['site'] = site
                old_values['assessed_by'] = request.user
                rev = models.SiteReview(**old_values)

                site = siteReviewForm.save(commit=False)
                rev.set_new_values(site)
                site.save(log=log)
                rev.save(log=log)
                siteReviewForm = forms.SiteReview(instance=site)

#               Deal with actors.
                sourcenames = []
                if site.visited_by:
                    names = site.visited_by.split(';')
                    for name in names:
                        sourcenames.append(name.strip())
                    sourcenames.append(site.visited_by.strip())

                if site.recorded_by:
                    names = site.recorded_by.split(';')
                    for name in names:
                        sourcenames.append(name.strip())

                if site.updated_by:
                    names = site.updated_by.split(';')
                    for name in names:
                        sourcenames.append(name.strip())

                sourcenames = set(sourcenames)
                sourcenames = list(sourcenames)

                for sourcename in sourcenames:
                    try:
                        a = models.Actor.objects.get(sourcename=sourcename)

                    except models.Actor.DoesNotExist:
                        a = models.Actor(sourcename=sourcename)
                        a.save()
                    a.sites.add(site)

                return redirect(site.url)

            else:
                context['notifications'].append(
                    "Site review form not valid.")
                
        elif argument == 'normalise':
            pass
        
        else:
            log_message = "Unknown call"
            if request.POST['command'] == 'stage':
                update.opstatus = "Staging"
                log_message = 'Status set to "Staging".'

            elif request.POST['command'] == 'stand':
                update.opstatus = "Standing"
                log_message = 'Status set to "Standing".'

            elif request.POST['command'] == 'work':
                update.opstatus = "Working"
                log_message = 'Status set to "Working".'

            elif request.POST['command'] == 'complete':
                update.opstatus = "Completed"
                log_message = 'Status set to "Completed".'

            elif request.POST['command'] == 'hold':
                update.opstatus = "Hold"
                log_message = 'Status set to "Hold".'

            log = (
                request.META['REMOTE_ADDR'],
                request.user.username,
                log_message,
            )
            update.save(log=log)
            context['notifications'].append(log_message)
            updates_page ='/nzaa/updates/' + request.user.username
            return redirect(updates_page)

    context['update'] = update
    context['title'] = site.nzaa_id + " | NZAA site record | archaeography.nz"
    context['commands'] = authority.commands(request, site, update)
    context['siteAssessForm'] = siteAssessForm
    context['siteReviewForm'] = siteReviewForm
    context['sitelist'] = site.get_siteLists()
    context['argument'] = argument

    context['h1'] = site.title
    context['subhead'] = "NZAA archaeological site record " + site.nzaa_id

    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def site_create(request):
    """Create a record in the NewSite table.

    The record will be identified by a code consisting of the Topo50
    grid area identifier and an iterating integer.

    """

    template = 'nzaa/CreateSite.html'
    tmp_id = None
    update_id = None

    context = build_context(request)
    context['notifications'] = []
    context['NewSiteForm'] = forms.NewSiteForm(
        initial={'opstatus': 'Working'}
    )
    context['main_form'] = MAIN_FORM
    context['buttons'] = ('create and make another', 'create and edit',)
    context['commands'] = authority.commands(request)
    context['title'] = "Create a new site record | archaeography.nz"
    username = request.user.username

    if request.POST:

        NewSiteForm = forms.NewSiteForm(request.POST)
        if NewSiteForm.is_valid():

            newsite = models.NewSite(**NewSiteForm.cleaned_data)

            point = Point(
                int(request.POST['easting']), int(request.POST['northing']),
                srid=2193,
            )
            sheet = Topo50grid.objects.get(geom__intersects=point)

            records = models.NewSite.objects.filter(
                topo50_sheet=sheet.identifier).order_by('-ordinal')
            if len(records) > 0:
                ordinal = records[0].ordinal + 1
            else:
                ordinal = 1
            
            identifier = sheet.identifier + '/' + str(ordinal)

            newsite.newsite_id = identifier
            newsite.owner = request.user.username
            newsite.created_by = request.user.username
            newsite.ordinal = ordinal
            newsite.topo50_sheet = sheet.identifier

            log = [
                request.META['REMOTE_ADDR'],
                request.user.username,
                'Creating record from site create form.',
            ]

            newsite.save(log=log)

            if request.POST['command'] == 'create and make another':
                context['notifications'].append(
                    "Created site record " + newsite.newsite_id
                )

                context['NewSiteForm'] = forms.NewSiteForm(request.POST)
                return render(request, 'nzaa/CreateSite.html', context)

            elif request.POST['command'] == 'create and edit':

                return redirect(newsite.url + '/edit/')

        else:

            context['notifications'].append("Your form didn't validate")

        context['updateMainForm'] = updateMainForm

    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def site_update(request, command):
    """Create a new update record for a site.

    """

    template = 'nzaa/UpdateEdit.html'
    site = None
    nzaa_id = request.path.replace('/update/', '')
    nzaa_id = nzaa_id.replace('/nzaa/', '')

    context = build_context(request)
    context['nzaa_id'] = nzaa_id

    username = request.user.username

    try:
        site = models.Site.objects.get(nzaa_id=nzaa_id)
    except models.Site.DoesNotExist:
        context['doesNotExist'] = True
        return render(request, 'nzaa/siteUpdate.html', context)

    context['h1'] = site.nzaa_id + " | NZAA site record"
    context['subhead'] = "New update record"
    context['title'] = context['h1']
    updatePanelForm = forms.UpdatePanel(instance=site)
    updateMainForm = forms.UpdateMain(instance=site)

    if request.POST:
        updatedata = {}
        updatedata.update(request.POST)

        ordinal = site.updates()[0].ordinal + 1
        update_id = site.nzaa_id + "-" + str(ordinal)

        updateForm = forms.UpdateFull(request.POST)

        if updateForm.is_valid():
            u = updateForm.save(commit=False)
            u.created = datetime.datetime.now()
            u.owner = request.user.username
            u.updated = datetime.datetime.now()
            u.site = site
            u.ordinal = ordinal
            u.update_id = update_id
            u.status = 'Pending'
            u.opstatus = 'Working'

            u.save()
            return redirect(os.path.join(u.url, 'edit'))

        else:
            context['notifications'].append('Your form did not validate.')

        updatePanelForm = forms.UpdatePanel(request.POST)
        updateMainForm = forms.UpdateMain(request.POST)

    context['site'] = site
    context['main_form'] = MAIN_FORM
    context['buttons'] = ('create',)
    context['updatePanelForm'] = updatePanelForm
    context['updateMainForm'] = updateMainForm

    context['commands'] = authority.commands(request, site)
    context['filekeeper_commands'] = authority.filekeeper_commands(
        request, site)

    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def sitelists(request, command):

    context = build_context(request)
    context['h1'] = 'NZAA archaeological site lists'
    context['title'] = "Site record lists | archaeography.nz"
    context['subhead'] = "All site lists"
    context['sitelists'] = None
    template = 'nzaa/Sitelists.html'
    sitelist = None

    context['jsortable'] = True
    context['main_form'] = MAIN_FORM

    context['buttons'] = []

    request.session['siteset'] = None
    siteset = {
        'setname': '',
        'seturl': os.path.join(settings.BASE_URL, command),
        'setlist': [],
    }

    try:
        id = int(command)
        sitelist = models.SiteList.objects.get(id=id)
        context['SiteListForm'] = forms.SiteList(instance=sitelist)
        if request.user.username == sitelist.owner:
            context['buttons'].append('save')
            if sitelist.sites.count():
                context['buttons'].append('remove selected')

    except ValueError:
        context['sitelists'] = models.SiteList.objects.filter(owner=command)
        context['subhead'] = 'Site lists belonging to ' + command
    except models.SiteList.DoesNotExist:
        pass

    if sitelist:

        if request.POST:

            if request.POST['command'] == 'delete this list':
                sitelist.delete()
                return redirect('/nzaa/sitelists/' + request.user.username)

            if request.POST['command'] == 'remove selected':
                sitelist.remove_sites(request.POST)

            if request.POST['command'] == 'new from selected':
                selected = ""
                for i in request.POST.keys():
                    if utils.is_siteid(i):
                        selected += i + ","
                return redirect('/nzaa/sitelist/create?addsites=' + selected)

            elif request.POST['command'] == 'save':
                f = forms.SiteList(request.POST, instance=sitelist)

                if f.is_valid():
                    s = f.save(commit=False)
                    s.modified_by = request.user.username
                    s.save()
                    context['SiteListForm'] = forms.SiteList(instance=s)

                    if request.POST['addsites']:
                        # Set capture=True to scrape site records.
                        sites, warnings = string2sites(
                            request.POST['addsites'])
                        for site in sites:
                            try:
                                sitelist.sites.add(site)
                            except IntegrityError:
                                print "IntegrityError"
                                pass
        context['title'] = ("Site list: " + sitelist.name + " | " +
                            context['title'])
        template = 'nzaa/Sitelist.html'
        context['sitelist'] = sitelist

        siteset['setname'] = sitelist.name
        siteset['seturl'] = sitelist.url
        siteset['setlist'] = list(sitelist.sites.values_list(
            'nzaa_id', flat=True))

        if sitelist.owner == request.user.username:
            context['buttons'].append('delete this list')

    # If there in no individual sitelist requested.
    else:
        siteset['setlist'] = []
        if not context['sitelists'].count():
            context['sitelists'] = models.SiteList.objects.all()
            context['subhead'] = "All site lists"

    context['commands'] = authority.commands(request, sitelist=sitelist)
    request.session['siteset'] = siteset
    context['breadcrumbs'] = build_breadcrumbs(request)

    return render(request, template, context)


@user_passes_test(authority.nzaa_member)
def tlas(request, command=None):
    """Tertitorial authorities."""

    template = 'nzaa/TLAs.html'
    context = build_context(request)
    context['commands'] = authority.commands(request)
    context['jsortable'] = True
    context['simpleSearch'] = forms.SimpleSearch

    context['breadcrumbs'] = build_breadcrumbs(request)
    return render(request, template, context)


# Legacy code, not checked. Seems to work.
@user_passes_test(authority.nzaa_member)
def update_edit(request, command):
    """Provide for making changes to an update record. """

    context = build_context(request)
    template = 'nzaa/UpdateEdit.html'

    try:
        u = models.Update.objects.get(update_id=command)
        site = u.site
        context['update'] = u
        context['site'] = site
    except models.Update.DoesNotExist:
        context['doesNotExist'] = True
        context['update_id'] = command
        return render(request, template, context)

    if not authority.edit_this_update(request.user, u):
        return redirect(u.url)

    context['h1'] = u.site.nzaa_id + " | NZAA site update record"

    username = request.user.username
    citation = request.user.username
    ipno = request.META['REMOTE_ADDR']

    context['commands'] = authority.commands(request, site, u)

    if context['filekeeper']:
        context['filekeeper_commands'] = authority.filekeeper_commands(
            request, site=site)

    updatePanelForm = forms.UpdatePanel(instance=u)
    updateMainForm = forms.UpdateMain(instance=u)
    fileUploadForm = forms.UploadFile()

    now = datetime.datetime.now()
    timestamp = unicode(now.replace(microsecond=0))

    if request.POST:

        updateFullForm = forms.UpdateFull(request.POST, instance=u)

        if updateFullForm.is_valid():
            u = updateFullForm.save(commit=False)

            u.updated = request.POST['updated']
            u.updated_by = request.POST['updated_by']
            u.modified_by = request.user.username

            if len(request.FILES) > 0:
                filename = str(request.FILES['filename']).replace(' ', '_')
                filepath = os.path.join(u.filespace_path(), filename)

                with open(filepath, 'wb+') as destination:
                    for chunk in request.FILES['filename'].chunks():
                        destination.write(chunk)

            log_message = "Saving update record from form."

            context['notifications'].append(
                timestamp + ", saving record.")
        else:
            context['notifications'].append(
                'Your form did not validate.')

        updatePanelForm = forms.UpdatePanel(instance=u)
        updateMainForm = forms.UpdateMain(instance=u)

        if request.POST['command'] == 'save':
            pass

        elif request.POST['command'] == 'stage':
            u.opstatus = "Staging"
            log_message = 'Status set to "Staging".'

        elif request.POST['command'] == 'stand':
            u.opstatus = "Standing"
            log_message = 'Status set to "Standing".'

        elif request.POST['command'] == 'work':
            u.opstatus = "Working"
            log_message = 'Status set to "Working".'

        elif request.POST['command'] == 'complete':
            u.opstatus = "Completed"
            log_message = 'Status set to "Completed".'

        elif request.POST['command'] == 'submit':
            u.status = 'Submitted'
            u.opstatus = None
            log_message = "Update record submitted for scrutiny."

        log = (ipno, username, log_message)

        u.save(log=log)

    context['main_form'] = MAIN_FORM
    context['buttons'] = ('save',) + u.buttons(request.user)
    context['title'] = u.update_id + " | edit site update | archaeography.nz"

    context['updatePanelForm'] = updatePanelForm
    context['updateMainForm'] = updateMainForm
    context['fileUploadForm'] = fileUploadForm

    return render(request, template, context)


# Legacy code, not checked.
@user_passes_test(authority.nzaa_member)
def update_submit(request, command):
    """Provide for an update record to be submitted for approval.
    """

    context = build_context(request)
    template = 'nzaa/UpdateEdit.html'

    try:
        u = models.Update.objects.get(update_id=command)
        site = u.site
        context['update'] = u
        context['site'] = site
    except models.Update.DoesNotExist:
        context['doesNotExist'] = True
        context['update_id'] = command
        return render(request, template, context)

    context['main_form'] = MAIN_FORM
    context['buttons'] = ('submit',)
    context['title'] = u.update_id + " | edit site update | archaeography.nz"

    context['commands'] = authority.commands(request, site, u)
    if context['filekeeper']:
        context['filekeeper_commands'] = authority.filekeeper_commands(
            request, site=site)

    context['archsiteLink'] = (
        settings.EDIT_SITE + u.site.nzaa_id, 'update this site record')

    if u.site.temp_id == u.site.nzaa_id:
        context['archsiteLink'] = (
            settings.CREATE_SITE, 'create a new site record')
        context['new_record'] = True
        context['newID_form'] = forms.NewID()

    if request.POST:
        log = (
            request.META['REMOTE_ADDR'],
            request.user.username,
            "Record submitted for filekeeper scrutiny.",
        )

        u.status = 'Submitted'
        u.opstatus = None

        newID_form = forms.NewID(request.POST)

        if u.site.temp_id == u.site.nzaa_id:
            if newID_form.is_valid():
                u.new_id = request.POST['new_id']

            else:
                context['newID_form'] = forms.NewID(request.POST)

                context['notifications'].append('The NZAA id is not valid.')
                return render(request, 'nzaa/upload.html', context)

        u.save(log=log)

        if u.site.temp_id == u.site.nzaa_id:
            change.accession(u.site.nzaa_id)

        return redirect('/nzaa/')

    return render(request, 'nzaa/upload.html', context)


# Legacy code, not checked. Seems to work.
@user_passes_test(authority.nzaa_member)
def user_updates(request, command=None):

    context = build_context(request)
    template = 'nzaa/UserUpdates.html'

    context['breadcrumbs'] = build_breadcrumbs(request, listtype='update')
    context['title'] = (
        "Site update records for user " + request.user.username +
        " | archaeography.nz"
    )

    updates = models.Update.objects.filter(owner=request.user.username)
    if updates.count() > 0:

        context['updates'] = updates
        context['jsortable'] = True

        context['pending_updates'] = updates.filter(status='Pending')
        context['submitted_updates'] = updates.filter(status='Submitted')
        context['returned_updates'] = updates.filter(status='Returned')
        context['sum_status'] = (
            len(context['pending_updates']) +
            len(context['submitted_updates']) +
            len(context['returned_updates'])
        )

        context['working_updates'] = updates.filter(opstatus='Working')
        context['staging_updates'] = updates.filter(opstatus='Staging')
        context['standing_updates'] = updates.filter(opstatus='Standing')
        context['held_updates'] = updates.filter(opstatus='Hold')
        context['completed_updates'] = updates.filter(
            opstatus='Completed')

    if request.GET:
        context['updates'] = []
        if ('status' in request.GET and request.GET['status'] == 'Submitted'):
            context['updates'] = context['submitted_updates']

        elif ('status' in request.GET and
              request.GET['status'] == 'Returned'):
            context['updates'] = context['returned_updates']

        elif ('opstatus' in request.GET and
              request.GET['opstatus'] == 'Working'):
            context['updates'] = context['working_updates']

        elif ('opstatus' in request.GET and
              request.GET['opstatus'] == 'Standing'):
            context['updates'] = context['standing_updates']

        elif ('opstatus' in request.GET and
              request.GET['opstatus'] == 'Completed'):
            context['updates'] = context['completed_updates']

        elif ('opstatus' in request.GET and
              request.GET['opstatus'] == 'Pending'):
            context['updates'] = context['pending_updates']

        context['SelectUpdateStatus'] = forms.SelectUpdateStatus(request.GET)

    context['commands'] = authority.commands(request)
    context['filekeeper_commands'] = authority.filekeeper_commands(request)

    return render(request, template, context)


# ----------------------------------------------------------------
# Ancilliary functions (not views).
#

def build_breadcrumbs(request, listtype=None):
    """Return a list of link/text tuples leading useful places.

    The useful places will vary. If you're looking at an NZMS260 sheet
    of record, next and previous will be the next and previous records
    on that sheet. If you have just clicked on a record on a sitelist,
    then next and previous will be next and previous from that list.

    """

    suffix = ''
    breadcrumbs = [
        (settings.BASE_URL, 'NZAA sites'),
    ]

#   Add the section links right after the home link.
    if 'sitelist' in request.path:
        breadcrumbs.append(
            (os.path.join(settings.BASE_URL, 'sitelists/'), 'site lists'),
        )
    elif '/actor' in request.path:
        breadcrumbs.append(
            (os.path.join(settings.BASE_URL, 'actors/'), 'actors'),
        )

    elif 'feature' in request.path:
        breadcrumbs.append(
            (os.path.join(settings.BASE_URL, 'features/'), 'features'),
        )

    elif '/newsites' in request.path:
        breadcrumbs.append(
            (os.path.join(settings.BASE_URL, 'newsites/'), 'new site records'),
        )

    elif '/nzaareg' in request.path:
        breadcrumbs.append(
            (os.path.join(settings.BASE_URL, 'nzaareg/'), 'nzaa regions'),
        )

    elif 'period' in request.path:
        breadcrumbs.append(
            (os.path.join(settings.BASE_URL, 'periods/'), 'periods'),
        )

    elif '/region' in request.path:
        breadcrumbs.append(
            (os.path.join(settings.BASE_URL, 'regions/'), 'regions'),
        )

    elif '/tla' in request.path:
        breadcrumbs.append(
            (os.path.join(settings.BASE_URL, 'tlas/'), 'territorial auths'),
        )

    path = request.path.replace(settings.BASE_URL, '')
    if path and path[-1] == '/':
        path = path[:-1]

#   This is all just to determine if there is a list of site
#   identifiers in the session variable.
    if (
            'siteset' in request.session.keys() and
            request.session['siteset'] and
            'setlist' in request.session['siteset'].keys() and
            request.session['siteset']['setlist']
    ):

        sites = request.session['siteset']['setlist']
        if len(sites):
            breadcrumbs.append((
                request.session['siteset']['seturl'],
                request.session['siteset']['setname'] +
                ' (' + str(len(sites)) + ')'
            ))

#       Are we looking at a site record?
        if utils.is_siteid(path):
            try:
                i = sites.index(path)

                if i == 0:
                    iprev = len(request.session['siteset']['setlist'])-1
                else:
                    iprev = i - 1

                breadcrumbs.append((
                    os.path.join(settings.BASE_URL, sites[iprev]),
                    sites[iprev],
                ))

                breadcrumbs.append((
                    os.path.join(settings.BASE_URL, sites[i]),
                    sites[i] + ' (' + str(i+1) + ' of ' +
                    str(len(sites)) + ')',
                ))

                if i == len(request.session['siteset']['setlist'])-1:
                    inext = 0
                else:
                    inext = i + 1

                breadcrumbs.append((
                    os.path.join(settings.BASE_URL, sites[inext]),
                    sites[inext],
                ))
            except ValueError:
                pass
#       Do we have a sublist?
        if request.GET:
            if 'next' in request.GET.keys() or 'last' in request.GET.keys():
                first = int(request.GET['first'])
                last = int(request.GET['last'])
                url = request.path

                bfirst = first - LIMIT
                if bfirst < 0:
                    bfirst = 0
                blast = bfirst + LIMIT

                before = (
                    url + '?first=' + str(bfirst) + '&last=' + str(blast),
                    str(bfirst) + ' to ' + str(blast)

                )

                present = (
                    url + '?first=' + str(first) + '&last=' + str(last),
                    str(first) + ' to ' + str(last)
                )

                afirst = last
                alast = afirst + LIMIT
                after = (
                    url + '?first=' + str(afirst) + '&last=' + str(alast),
                    str(afirst) + ' to ' + str(alast)

                )

                breadcrumbs.append(before)
                breadcrumbs.append(present)
                breadcrumbs.append(after)

    return breadcrumbs


def build_context(request):
    """Return a dictionary containing site infrastructure structures.

    Start with the home context variable, which contains site-wide
    infrastructure, and add what is common to the archlib application.

    """

    context = home.views.build_context(request)
    context['nav'] = 'nzaa/nav.html'
    context['stylesheet'] = 'css/nzaa.css'
    context['notifications'] = []
    context['loginform'] = None
    context['filekeeper'] = authority.filekeeper(request.user)
    context['member'] = authority.nzaa_member(request.user)
    context['buttons'] = None
    context['URL'] = settings.BASE_URL
    context['simpleSearch'] = forms.SimpleSearch
    
    if authority.nzaa_member:
        context['authorised'] = True

    return context


# Legacy code, not checked.

# This should be changed, to provide a breadcrumbs object, for use
# when single site records are being viewed. That is, when not viewing
# a list or group of site records.
def site_sequence(nzaa_id):
    """Return list of (link, text) tuples linking prev & next identifiers.
    """

    (sheet, ordinal) = nzaa_id.split('/')
    ordinal = int(ordinal)

    ord_prev = ordinal - 1
    ord_next = ordinal + 1

    link_sheet = os.path.join(settings.BASE_URL, sheet)
    text_sheet = sheet

    text_prev = sheet + "/" + str(ord_prev)
    link_prev = os.path.join(settings.BASE_URL, text_prev)

    link = os.path.join(settings.BASE_URL, nzaa_id)
    text = nzaa_id

    text_next = sheet + "/" + str(ord_next)
    link_next = os.path.join(settings.BASE_URL, text_next)

    if ordinal == 1:
        text_prev = sheet + "/" + "1"
        link_prev = os.path.join(settings.BASE_URL, text_prev)

    result = [
        (link_sheet, text_sheet),
        (link_prev, text_prev),
        (link, text),
        (link_next, text_next),
    ]

    return result


def string2sites(string, capture=False):
    """Return a list of site identifiers from a string.

    String may contain a comma-separated list of identifiers, in
    single or double quotes, or no quotes.

    When capture is set True, test for a record matching the resulting
    id exists. If not, then scrape it.

    """
    sites = []
    warnings = []

    bits = string.upper().split(',')

    for bit in bits:
        bit = bit.strip()
        bit = bit.replace('"', '')
        bit = bit.replace("'", "")

        if capture:
            try:
                site = models.Site.objects.get(nzaa_id=bit)
                sites.append(bit)
            except models.Site.DoesNotExist:
                s = scrape.Scrape([bit])
                try:
                    site = models.Site.objects.get(nzaa_id=bit)
                    sites.append(bit)
                except models.Site.DoesNotExist:
                    pass
        else:

            if utils.is_siteid(bit):
                sites.append(bit)
            else:
                warnings.append(bit + " : Invalid site id")

    return sites, warnings
