from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F
from django.contrib.gis.geos import Polygon, MultiPolygon

import authority
import home.views
import forms
import models
import nzaa.analyse
import nzaa.authority
import settings
import utils

MAIN_FORM = {
    'id': 'geolib',
    'action': '',
    'method': 'POST',
    'class': 'mainForm',
}


def airphoto(request, command):

    context = build_context(request)
    template = 'geolib/airphoto.html'

    survey = None
    run = None
    frame = None
    form = None

    context['command'] = command
    context['found'] = None
    context['edit'] = False
    h1 = 'Historic aerial photo collection'
    context['subhead'] = 'selected from the NZ national collection '
    context['subhead'] += 'available at http://retrolens.nz'
    context['jsortable'] = True
    context['nzaa_member'] = nzaa.authority.nzaa_member(request.user)

    context['surveys'] = models.AerialSurvey.objects.all()
    context['runs'] = models.AerialRun.objects.all()
    context['frames'] = models.AerialFrame.objects.all()
    context['georef'] = models.AerialFrame.objects.exclude(
        status__isnull=True)

    siteset = None
    setlist = None

    if command:

        parts = command.split('/')
        survey_id = parts[0]

        if parts[-1][-4:] == 'edit':
            context['edit'] = True
            parts.pop()
            context['buttons'] = ('save',)
            context['main_form'] = MAIN_FORM

        try:
            survey = models.AerialSurvey.objects.get(identifier=survey_id)
            form = 'survey'
            context['found'] = True
            h1 = survey.identifier + " | Historic aerial survey "
            if context['edit']:
                context['form'] = forms.AerialSurveyForm(instance=survey)
        except models.AerialSurvey.DoesNotExist:
            context['found'] = False
            survey = survey_id
            h1 = 'Aerial survey not found (' + survey + ')'

    if context['found']:
        if len(parts) > 1:
            run_id = survey_id + '/' + parts[1]
            try:
                run = models.AerialRun.objects.get(identifier=run_id)
                form = 'run'
                context['found'] = True
                h1 = run.identifier + " | Historic aerial survey run"
                if context['edit']:
                    context['form'] = forms.AerialRunForm(instance=run)
            except models.AerialRun.DoesNotExist:
                context['found'] = False
                run = run_id
                h1 = 'Aerial survey run not found (' + survey_id + ')'
    # This is weird. But you have to have the row before you can get
    # the frame.
    if context['found']:
        if len(parts) > 2:
            frame_id = run_id + '/' + parts[2]
            try:
                frame = models.AerialFrame.objects.get(identifier=frame_id)
                sites = frame.sites()
                form = 'frame'
                h1 = frame.identifier + " | Historic aerial photograph"
                if frame.sites():
                    context['sites'] = frame.sites()
                    analysis = nzaa.analyse.Site(context['sites'])
                    context['sites_by_lgcy_type'] = \
                        analysis.count_by_lgcy_type()
                    siteset = {
                        'setname': frame.identifier,
                        'seturl': frame.url,
                        'setlist': setlist,
                    }
                    setlist = list(sites.values_list('nzaa_id', flat=True))
                    identifiers = ""
                    for i in setlist:
                        identifiers += "'" + i + "', "
                    context['identifiers'] = identifiers[:-2]

                if context['edit']:
                    context['form'] = forms.AerialFrameForm(instance=frame)

                if request.GET:
                    (groupname, sites) = nzaa.analyse.site_subselect(
                        request, frame.sites())
                    context['sites'] = sites
                    context['groupname'] = groupname

            except models.AerialFrame.DoesNotExist:
                context['found'] = False
                frame = frame_id
                h1 = 'Aerial survey frame  not found (' + survey.id + ')'

    if request.POST:
        if form == 'survey':
                context['form'] = forms.AerialSurveyForm(
                    request.POST, instance=survey)
        elif form == 'run':
                context['form'] = forms.AerialRunForm(
                    request.POST, instance=run)
        elif form == 'frame':
            context['form'] = forms.AerialFrameForm(
                    request.POST, instance=frame)

        if context['form'].is_valid():
            context['form'].save()
            context['notifications'].append('Saving ' + form)

    rand = 456

    context['h1'] = h1
    context['title'] = context['h1'] + " | archaeography.nz"
    context['survey'] = survey
    context['run'] = run
    context['frame'] = frame
    if len(context['frames']) > rand:
        context['featured'] = context['frames'][rand]

    request.session['siteset'] = siteset
    context['breadcrumbs'] = build_breadcrumbs(request)

    if survey:
        context['breadcrumbs'].append((survey.url, survey.identifier))
    if run:
        context['breadcrumbs'].append((run.url, run.name))
    if frame:
        context['breadcrumbs'].append((frame.url, frame.identifier))
    return render(request, template, context)


def airphoto_newframe(request):
    """Provide forms to create a frame record."""

    survey = None
    run = None
    frame = None

    context = build_context(request)
    template = 'geolib/airphoto/newframe.html'
    context['h1'] = "New aerial photo frame record"
    context['title'] = context['h1'] + " | archaeography.nz"
    context['buttons'] = ('new frame',)
    context['main_form'] = MAIN_FORM
    responses = None
    frameForm = forms.AerialNewFrameForm()

    if request.POST:
        responses = []
        context['notifications'] = []
        data = {}
        frameForm = forms.AerialNewFrameForm(request.POST)

        if frameForm.is_valid():
            identifier = request.POST['identifier']
            creator = utils.CreateAirphotoRecords(identifier)

            data = request.POST

            if creator.frame:
                return redirect(creator.frame.url)

            elif creator.run:
                data['run'] = creator.run
                responses.append(('note', 'Survey & run records exist'))

            elif creator.survey:
                data['survey'] = creator.survey
                responses.append(('note', 'Survey record exists'))

            else:
                ids = identifier.split('/')
                sn = ids[0]
                data['id'] = sn

                context['buttons'] = ('new survey and frame',)
                context['newSurveyForm'] = forms.AerialNewSurveyForm(data)
                context['newFrameForm'] = forms.AerialNewFrameForm(data)

                context['notifications'].append(
                    'Please complete a survey record')

                if not data['command'] == 'new survey and frame':
                    return render(request, template, context)

            creator.create_records(data)
            context['notifications'].extend(creator.notifications)
            responses.append(('url', creator.frame.get_retrolens_url()))
            responses.append(('run fp', creator.run.filespace()))

        else:
            context['notifications'].append(
                'Please attend to errors in the form.')

    context['newFrameForm'] = frameForm
    context['responses'] = responses

    return render(request, template, context)


def cadastre(request, command):

    context = build_context(request)
    template = 'geolib/cadastre.html'
    context['h1'] = "NZ cadastral data"
    context['title'] = context['h1'] + " | archaeography.nz"
    context['subhead'] = 'Property parcels from Land Information New Zealand'
    context['parcel'] = None
    context['parcels'] = None
    context['jsortable'] = True
    request.session['siteset'] = None
    parcel = None
    siteset = None
    terms = None

    if command:
        try:
            int(command)
            try:
                parcel = models.Cadastre.objects.get(id=command)
                context['parcel'] = parcel
            except models.Cadastre.DoesNotExist:
                context['notifications'].append('Parcel not found')

        except ValueError:
            context['notifications'].append('Identifier not understood')

    if request.GET:
        parcels = None
        if request.GET['terms']:
            terms = request.GET['terms']
            parcels = models.Cadastre.objects.filter(appellation=terms)

        if parcels:
            if parcels.count() == 1:
                parcel = parcels[0]
            else:
                context['parcels'] = parcels
        context['terms'] = terms

    if parcel:
        print "IF PARCEL"
        context['parcel'] = parcel
        setname = str(parcel.appellation)
        if len(setname) > 10:
            setname = parcel.appellation[0:9] + '...'

        siteset = {
            'setname': setname,
            'seturl': parcel.url,
            'setlist': [],
        }

        adjacent = list(parcel.sites_adjacent().values_list(
            'nzaa_id', flat=True))
        buf_dist = list(parcel.sites_buffer().values_list(
            'nzaa_id', flat=True))
        setlist = buf_dist + adjacent
        setlist = set(setlist)
        siteset['setlist'] = list(setlist)

    request.session['siteset'] = siteset
    context['breadcrumbs'] = build_breadcrumbs(request)
    return render(request, template, context)


def homepage(request):

    context = build_context(request)
    template = 'geolib.html'

    context['h1'] = "Geographic data library"
    context['title'] = context['h1'] + " | archaeography.nz"
    context['subhead'] = "Maps and plans, aerial photos,"
    context['subhead'] += " and remote sensing coverage"

    return render(request, template, context)


def lidar(request, command):

    context = build_context(request)
    template = 'geolib/lidar.html'

    context['command'] = command
    context['h1'] = 'Lidar elevation data'
    context['subhead'] = '1 m resolution elevation data; DEMs and hillshades'
    context['series'] = models.LidarSet.objects.all()
    context['jsortable'] = True
    context['nzaa_member'] = nzaa.authority.nzaa_member(request.user)

    tile = None
    series = None
    siteset = None

    if command:
        bits = command.split('/')
        series_id = bits[0]

        try:
            series = models.LidarSet.objects.get(identifier=series_id)
        except models.LidarSet.DoesNotExist:
            pass

        if len(bits) > 1:
            identifier = bits[1]
            try:
                tile = models.LidarTile.objects.filter(
                    series=series_id, identifier=identifier
                )
                sites = tile[0].sites()
                template = 'geolib/lidar/tile.html'
                context['h1'] = str(tile)
                context['subhead'] = ""
                context['sites'] = tile[0].sites()
                analysis = nzaa.analyse.Site(context['sites'])
                context['sites_by_lgcy_type'] = (
                    analysis.count_by_lgcy_type())

                if request.GET:
                    (groupname, sites) = nzaa.analyse.site_subselect(
                        request, tile.sites())
                    context['sites'] = sites
                    context['groupname'] = groupname

                siteset = {
                    'setname': tile[0].identifier,
                    'seturl': tile[0].url,
                    'setlist': list(
                        sites.values_list('nzaa_id', flat=True)
                    ),
                }
            except models.LidarTile.DoesNotExist:
                template = 'geolib/lidar/TileNotFound.html'
                context['h1'] = "Orthophoto tile not found"
                context['subhead'] = "No record of tile " + command

    else:
        context['allseries'] = models.LidarSet.objects.all()

    context['series'] = series

    request.session['siteset'] = siteset
    context['breadcrumbs'] = build_breadcrumbs(request)

    if series:
        context['breadcrumbs'].append((series.url, series.identifier))
    if tile:
        context['breadcrumbs'].append((tile[0].url, tile[0].identifier))

    context['tile'] = tile
    context['title'] = context['h1'] + " |  archaeography.nz"
    return render(request, template, context)


def orthophoto(request, command):

    series = None
    siteset = None
    tile = None

    context = build_context(request)
    template = 'geolib/orthophoto.html'
    context['command'] = command
    context['h1'] = 'Orthorectified aerial imagery'
    context['subhead'] = 'Slightly different thing to aerial photography'
    context['jsortable'] = True
    context['nzaa_member'] = nzaa.authority.nzaa_member(request.user)

    if command:
        bits = command.split('/')
        series_id = bits[0]
        try:
            series = models.OrthoSet.objects.get(identifier=series_id)
            context['series'] = series
        except models.OrthoTile.DoesNotExist:
            pass

        if len(bits) > 1:
            identifier = bits[1]
            try:
                tile = models.OrthoTile.objects.get(
                    series__identifier=series_id, identifier=identifier
                )
                sites = tile.sites()
                template = 'geolib/orthophoto/tile.html'
                context['h1'] = str(tile)
                context['subhead'] = "orthorectified aerial imagery "

                context['sites'] = tile.sites()
                analysis = nzaa.analyse.Site(context['sites'])
                context['sites_by_lgcy_type'] = (
                    analysis.count_by_lgcy_type())

                if request.GET:
                    (groupname, sites) = nzaa.analyse.site_subselect(
                        request, tile.sites())
                    context['sites'] = sites
                    context['groupname'] = groupname

                siteset = {
                    'setname': tile.identifier,
                    'seturl': tile.url,
                    'setlist': list(
                        sites.values_list('nzaa_id', flat=True)
                    ),
                }
            except models.OrthoTile.DoesNotExist:
                template = 'geolib/orthophoto/TileNotFound.html'
                context['h1'] = "Orthophoto tile not found"
                context['subhead'] = "No record of tile " + command
    else:
        # No command, get the list of all series.
        context['allseries'] = models.OrthoSet.objects.all()

    request.session['siteset'] = siteset
    context['breadcrumbs'] = build_breadcrumbs(request)
    if series:
        context['breadcrumbs'].append(
            (series.url, series.identifier))
    if tile:
        context['breadcrumbs'].append(
            (tile.url, tile.identifier))

    context['tile'] = tile
    context['title'] = context['h1'] + " |  archaeography.nz"

    return render(request, template, context)


def search(request, command):
    """ """


def topomap(request, command):
    """Topographic maps collection.

    """

    tile = "Topographic map collection"
    sheet = None
    series = None
    geotif = None
    context = build_context(request)
    template = 'geolib/topomap.html'
    context['command'] = command
    context['h1'] = 'Topographic map collection'
    context['title'] = context['h1'] + " | archaeography.nz"
    context['subhead'] = 'Topographic maps from NZ'
    context['series'] = models.TopoMapSeries.objects.all()
    context['jsortable'] = True
    context['nzaa_member'] = nzaa.authority.nzaa_member(request.user)
    context['command'] = command

    if command:

        if command == 'geotif/':
            return render(request, template, context)

        if '.tif' in command:
            try:
                geotif = models.TopoMapFile.objects.get(
                    filename=command)
                sheet = geotif.sheet
                context['sheet'] = sheet
                context['geotif'] = geotif
                context['sites'] = sheet.sites()

            except models.TopoMapFile.DoesNotExist:
                pass

        bits = command.split('/')

        if len(bits) == 1:
            try:
                series = models.TopoMapSeries.objects.get(series=command)
                context['sere'] = series
            except models.TopoMapSeries.DoesNotExist:
                pass
        elif len(bits) == 2:
            try:
                sheet = models.TopoMap.objects.get(id=int(bits[1]))
                sites = sheet.sites()

                analysis = nzaa.analyse.Site(sites)
                context['sites_by_lgcy_type'] = (
                    analysis.count_by_lgcy_type())

                if request.GET:
                    (groupname, sites) = nzaa.analyse.site_subselect(
                        request, sheet.sites())
                    context['groupname'] = groupname

                setlist = list(sites.values_list('nzaa_id', flat=True))

                siteset = {
                    'setname': sheet.name,
                    'seturl': sheet.url,
                    'setlist': setlist,
                }

                request.session['siteset'] = siteset
                context['breadcrumbs'] = build_breadcrumbs(request)
                context['breadcrumbs'].append((sheet.url, sheet.sheet_id))

                context['sites'] = sites

            except models.TopoMap.DoesNotExist:
                pass

    context['breadcrumbs'] = build_breadcrumbs(request)
    if series:
        context['breadcrumbs'].append((series.url, series.series))
    if sheet:
        context['breadcrumbs'].append((sheet.series.url, sheet.series.series))
        context['breadcrumbs'].append((sheet.url, sheet.sheet_id))

    context['sheet'] = sheet
    context['geotif'] = geotif

    return render(request, template, context)


# ------------------------------------------------------------------
def build_context(request):
    """Return a dictionary containing site infrastructure structures.

    Start with the home context variable, which contains site-wide
    infrastructure, and add what is common to the archlib application.

    """

    context = home.views.build_context(request)

    context['commands'] = authority.commands(request)
    context['librarian'] = authority.librarian(request.user)
    context['librarian_commands'] = authority.librarian_commands(request)
    context['simpleSearch'] = forms.SimpleSearch()
    context['nav'] = 'geolib/nav.html'
    context['stylesheet'] = None
    context['notifications'] = []
    context['loginform'] = None
    context['buttons'] = None
    context['URL'] = settings.BASE_URL

    return context


def build_breadcrumbs(request):
    """Return a list of (link, text) tuples giving useful navigations.
    """

    breadcrumbs = [
        ('/geolib', '/geolib'),
    ]

    if 'airphoto' in request.path:
        breadcrumbs.append(('/geolib/airphoto', 'airphoto'))

    if 'cadastre' in request.path:
        breadcrumbs.append(('/geolib/cadastre', 'cadastre'))

    if 'lidar' in request.path:
        breadcrumbs.append(('/geolib/lidar', 'lidar'))

    if 'ortho' in request.path:
        breadcrumbs.append(('/geolib/ortho', 'orthphotos'))

    if 'topo' in request.path:
        breadcrumbs.append(('/geolib/topo', 'topo maps'))

    return breadcrumbs
