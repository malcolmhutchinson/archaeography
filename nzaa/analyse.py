"""Analysis of lists of archaeological site records and updates.

This module provides analytical tools for acting on query objects of
site or update records. Given a queryset of site records, an object of
the site class will give you numbers by type, average quality
assessments, etc. New methods added as needed.

"""
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q, Count
from django.contrib.gis.geos import Point, MultiPoint
from django.contrib.gis.geos import Polygon, MultiPolygon

from itertools import chain
import markdown2 as markdown
import textwrap

import settings
import models
import geolib.models


class Normalise():
    """Analyse a Site record for normalisation.

    Look at the long fields description and condition, and pick out
    lines which fit the pattern for update records in ArchSite.

    Provide a list of updates with author and date. We should be able
    to tell if they are field visits or not.

    Separate the text into updates, by looking for this as the first
    characters in a line:

        Updated 09/04/2015 
    or

        Updated: 09/04/2015

    We could do it with an RE. or I could just match "Updated" as the
    first characters. Go the easy way first, and get some immediate
    results.

    """

    def __init__(self, site):
        self.site = site


    def find_dates(self):
        
        description = self.site.update0().description
        condition = self.site.update0().condition

        suggestions = []

        for line in description.split('\n'):
            date = ''
            name = ''
            update_type = ''
            line = line.strip()
            if line[:6].lower() == 'update': 
                words = line.split(' ')
                date = words[1]
                suggestions.append([date, name, update_type])

        return suggestions

    def find_updates(self):
        description = self.site.update0().description
        condition = self.site.update0().condition
        lines = []
        updates = []
        store = []

        for line in description.split('\n'):
            line = textwrap.fill(line.strip())

            if line[:6].lower() == 'update':
                updates.append(store)
                store = []
                
            store.append(line)
            
        for line in condition.split('\n'):
            line = textwrap.fill(line.strip())

            if line[:6].lower() == 'update':
                updates.append(store)
                store = []
                
            store.append(line)
            
        return updates[1:]








class Cadastre():
    """Analysis of cadastral parcels affected by sites.

    Instantiate with a queryset of Site objects. Returns the set of
    cadastre affected by proximity.

    Generates sets of cadastre from contact with the geometry fields
    in the supplied set of Site records.

        point_parcels

    Done by creating a MultiPoint object,then selecting cadastre
    which intersect with that.

    """

    sites = None
    point_parcels = None
    poly_parcels = None

    def __init__(self, sites):
        self.sites = sites
        self.iterate_sites(sites)

    def iterate_sites(self, sites):

        points = MultiPoint(sites[0].geom)
        polys = sites[0].geom_poly

        for site in sites[1:]:
            points = points.union(site.geom)
            polys = polys.union(site.geom_poly)

        self.point_parcels = geolib.models.Cadastre.objects.filter(
            geom__intersects=points)
        self.poly_parcels = geolib.models.Cadastre.objects.filter(
            geom__intersects=polys)


class MapSite():
    """All the required variables for a MapFile.

    Consume a Site object. Produce values for all the vairables
    required to construct a map of the site.

    """

    def __init__(self, site):
        self.site = site

    def extent(self):

        scale = 3000

        minx = self.site.easting - scale
        miny = self.site.northing - scale
        maxx = self.site.easting + scale
        maxy = self.site.northing + scale
        
        return str(minx) + ' ' + str(miny) + ' ' + str(maxx)  + ' ' + str(maxy)

    def linz_key(self):
        return settings.LINZ_KEY
    
    def password(self):
        return settings.MACHINE[1]

    def projection(self):
        proj = "        'proj=nztm\n"
        proj += "        'ellips=GRS80'\n"
        proj += "        'datum=NZGD2000'\n"
        proj += "        'units=m'"

        return proj
        
    def size_x(self):
        return "1024"

    def size_y(self):
        return "768"

    def username(self):
        return settings.MACHINE[0]

class Site():

    """Analyse lists of site records.

    Consumes a Django queryset of site records. Provides a set of
    methods interrogating that queryset on various criteria.

    Since some of these functions may be costly, they should only be
    called when needed, and not used to populate general statistical
    fields.

    If it has to iterate once throught the queryset, then it sould
    compute and store all the operations requiring an iteration. This
    will be much more efficient than iterating through potently tens
    of thousands of records several times to collect various bits of
    statistical data.

    """
    sitelist = None
    assessed = None
    dated = None

    store_site_assessment = None

    def __init__(self, sitelist):
        self.sitelist = sitelist

    def assess_by_sheet(self):
        if self.store_site_assessment:
            return self.store_site_assessment

        self.iterate_queryset()
        return self.store_site_assessment

    def assessment(self):
        """Provide a summary of quality assessments. """

        total = self.sitelist.count()
        if not total:
            return None

        assessed = self.sitelist.exclude(record_quality=None)
        count_assd = float(assessed.count())
        pc_assd = int((count_assd / total) * 100)

        comp = None
        pc_comp = None
        adequate = None
        pc_adequate = None
        thin = None
        pc_thin = None
        sparse = None
        pc_sparse = None
        trivial = None
        pc_trivial = None

        if count_assd:
            comp = assessed.filter(record_quality='comprehensive').count()
            pc_comp = int((float(comp) / count_assd) * 100)

            adequate = assessed.filter(record_quality='adequate').count()
            pc_adequate = int((float(adequate) / count_assd) * 100)

            thin = assessed.filter(record_quality='thin').count()
            pc_thin = int((float(thin) / count_assd) * 100)

            sparse = assessed.filter(record_quality='sparse').count()
            pc_sparse = int((float(sparse) / count_assd) * 100)

            trivial = assessed.filter(record_quality='trivial').count()
            pc_trivial = int((float(trivial) / count_assd) * 100)

        assessment = {
            "total": total,
            "assessed": int(count_assd),
            "remaining": total - int(count_assd),
            "pc_assd": pc_assd,
            "adequate": adequate,
            "pc_adequate": pc_adequate,
            "comp": comp,
            "pc_comp": pc_comp,
            "thin": thin,
            "pc_thin": pc_thin,
            "sparse": sparse,
            "pc_sparse": pc_sparse,
            "trivial": trivial,
            "pc_trivial": pc_trivial,
        }

        return assessment

    def count(self):
        return self.sitelist.count()

    def count_by_type(self):
        """Return a dictionary of site types with a count of each type."""

        sl = self.sitelist.order_by('site_type')
        c = sl.values('site_type').annotate(cnt=Count('site_type'))
        return c

    def count_by_lgcy_type(self):
        """Return a dictionary of site types with a count of each type."""

        sl = self.sitelist.order_by('lgcy_type')
        c = sl.values('lgcy_type').annotate(cnt=Count('lgcy_type'))
        return c

    def count_by_ethnicity(self):
        """Return a dictionary of ethnicity values."""

        sl = self.sitelist.order_by('ethnicity')
        c = sl.values('ethnicity').annotate(cnt=Count('ethnicity'))
        return c

    def count_by_period(self):
        """Return a dictionary of period values."""

        sl = self.sitelist.order_by('period')
        c = sl.values('period').annotate(cnt=Count('period'))
        return c

    def by_decade(self):

        """Return a tuple containing year, count values from date recorded.

        Acting on a subset of the sitelist which contains recorded
        data values, determine the earliest and latest records, then
        interate through each year, providing a count of records for
        each one.

        """

        years = []
        decade = {}
        decades = []

        dated = self.sitelist.exclude(
            recorded__isnull=True).order_by('recorded')

        firstyear = dated[0].recorded.year
        lastyear = dated.reverse()[0].recorded.year

        dcount = 0
        for y in range(firstyear, lastyear + 1):
            r = dated.filter(recorded__year=y).count()
            years.append((y, r))

            dec = str(y)[0:3] + '0'
            dec = int(dec)

            if dec in decade.keys():
                decade[dec] += r
            else:
                decade[dec] = r

        for key in sorted(decade.keys()):
            decades.append((key, decade[key]))

        return years, decades

    def by_date(self):
        """Return a dictionary of values associated with dates.

        earliest
        latest

        """

        not_updated_by = []
        not_visited_by = []
        not_updated = []
        not_visited = []

        dated = self.sitelist.exclude(
            recorded__isnull=True).order_by('recorded')

        dates = {
            'dated': dated.count(),
            'undated': self.count() - dated.count(),
            'earliest': dated[0],
            'latest': dated.reverse()[0],
            'no_recorded': self.sitelist.filter(
                recorded__isnull=True).count(),
            'no_recorded_by': self.sitelist.filter(
                recorded_by__isnull=True).count(),
            'no_updated': self.sitelist.filter(
                updated__isnull=True).count(),
            'no_updated_by': self.sitelist.filter(
                updated_by__isnull=True).count(),
            'no_visited': self.sitelist.filter(
                visited__isnull=True).count(),
            'no_visited_by': self.sitelist.filter(
                visited_by__isnull=True).count(),
            'no_quality': self.sitelist.filter(
                record_quality=None).count(),
            'not_updated': self.sitelist.filter(
                updated_by='Not updated').count(),
            'not_visited': self.sitelist.filter(
                visited_by='Not visited').count()
        }

        return dates

    def by_type(self):
        """Provide a table of site types and counts.

        This is returned as a list of (count, site_type) tuples,
        sorted with the most frequent type at the top.

        """

        types = []
        sites = self.sitelist.distinct('site_type').order_by('site_type')

        for site in sites:
            count = self.sitelist.filter(site_type=site.site_type).count()
            types.append((count, site.site_type))

        types = sorted(types, reverse=True)

        return types

    def find_skipped_numbers(self):
        """Intended for use with NZMS sheet values.

        Determine the unique set of sheet values. For each one of
        these, find the highest ordinal number. Iterate through an
        integer count from 1 to that number, recording all the numbers
        which are missing from the set.

        """

        skipped = []
        earliest = 1

        sheets = self.sitelist.distinct('nzms_sheet')
        for sheet in sheets:
            sites_on_sheet = self.sitelist.filter(
                nzms_sheet=sheet.nzms_sheet).order_by('-ordinal')
            latest = sites_on_sheet[0].ordinal

            for i in range(earliest, latest):
                try:
                    r = self.sitelist.get(ordinal=i)
                except:
                    skipped.append(sheet.nzms_sheet + '/' + str(i))

        return skipped

    def find_primary_waterways(self):
        """Return a dictionary listing nzaa_id, waterway, distance.

        The dictionary is keyed by nzaa_id"""

        output = {}
        waterways = geolib.models.Waterways.objects.all()

        for site in self.sitelist:
            table = []
            for way in waterways:
                name = way.base_name
                distance = site.geom.distance(way.geom)
                table.append((distance, name))
            table = sorted(table)
            output[site.nzaa_id] = table[0]

        return output

    def iterate_queryset(self):
        """Compute a table of assessment data by NZMS sheet."""

        sheets = self.sitelist.distinct('nzms_sheet')
        assessment = []

        for sheet in sheets:
            sheet_id = sheet.nzms_sheet
            records = self.sitelist.filter(nzms_sheet=sheet.nzms_sheet).count()
            assessed = self.sitelist.filter(
                nzms_sheet=sheet.nzms_sheet).exclude(
                    record_quality=None).count()
            remaining = records - assessed
            percent = int((assessed / float(records)) * 100)
            assessment.append((
                sheet_id, records, assessed, remaining, percent))

        self.store_site_assessment = assessment

    def missing_numbers(self):
        """Return a list of identifiers which don't have records.

        This should only work on sets where number of distinct values
        for nzms_sheet = 1.

        This is costly. It hits the DB once for every ordinal number
        on a sheet. That can be up to several thousand individual
        queries.

        """

        if self.sitelist.distinct('nzms_sheet').count() != 1:
            return None

        p = self.sitelist.order_by('-ordinal')
        sheet = self.sitelist[0].nzms_sheet
        top = p[0].ordinal
        missing = []

        for ordinal in range(1, top):
            id = sheet + '/' + str(ordinal)
            try:
                s = models.Site.objects.get(nzaa_id=id)
            except models.Site.DoesNotExist:
                missing.append(id)

        return missing

    def waterway_distances(self):
        """Generate a dictionary with distance statistics.

        Produce a dictionary structure containing aggregate
        statistics, including sites sorted by distance, .

        The returned structure contains these elments:

            'by_waterway': [
                (waterway_name, 'count', 'percent' 'distance'),
            ]

            'by_distance': [
                (distance (m), nzaa_id, waterway_name),
            ]

            'count_waterways': int,

            'furthest_id': nzaa identifier,

            'waterways': {
                waterway_name: [
                    (nzaa_id, distance)
                ]
            },
            'total_count': int

        """

        output = {
            'count_waterways': None,
            'by_waterway': None,
            'by_distance': None,
        }

        by_waterway = []
        by_distance = []
        count_sites = self.sitelist.count()

        waterways = {}
        distances = self.find_primary_waterways()

        for site in distances.keys():
            nzaa_id = site
            distance = distances[site][0]
            waterway = distances[site][1]

            # This to populate a table of waterways.
            if waterway not in waterways.keys():
                waterways[waterway] = [(site, distance)]
            else:
                waterways[waterway].append((site, distance))

            # Populate a table of sites sorted by distance.
            by_distance.append((int(distance), site, waterway))

        output['by_distance'] = sorted(by_distance, reverse=True)

        total_count = 0
        total_dist = 0
        percent = 0.0

        closest = 10000000
        furthest = 0

        for item in sorted(waterways.keys()):

            sum_dist = 0
            name = item
            count = len(waterways[item])

            for dist in waterways[item]:
                if dist[1] > furthest:
                    furthest_id = dist[0]
                    furthest = dist[1]
                if dist[1] < closest:
                    closest_id = dist[0]
                    closest = dist[1]

                sum_dist += dist[1]

            total_dist += sum_dist
            percent = int((float(count) / count_sites) * 100)
            av_dist = int(sum_dist / count)

            by_waterway.append((name, count, percent, av_dist))
            total_count += count

        output['by_waterway'] = by_waterway

        output['total_count'] = total_count
        output['count_waterways'] = len(waterways.keys())
        output['waterways'] = waterways
        output['overall_av'] = int(total_dist / total_count)
        output['closest_id'] = closest_id
        output['closest_dist'] = int(closest)
        output['furthest_id'] = furthest_id
        output['furthest_dist'] = int(furthest)

        return output


class User():
    """User class provides lists of a user's records.

    Consumes a request.user object. Provides lists of update records,
    siteList objects, and statistics about this user.

    """

    user = None

    live_updates = None
    pending_updates = None
    submitted_updates = None
    returned_updates = None

    def __init__(self, user):

        self.user = user
        self.live_updates = models.Update.objects.filter(
            owner=str(user.username))

        self.pending_updates = self.live_updates.filter(status='Pending')
        self.submitted_updates = self.live_updates.filter(status='Submitted')
        self.returned_updates = self.live_updates.filter(status='Returned')

    def status(self, status):
        """Return a list of update records of given status."""

        return self.live_updates.filter(status=status)

    def opstatus(self, opstatus):
        """Return a list of update records of given status."""

        return self.live_updates.filter(opstatus=opstatus)

    def sitelists_owned(self):
        """Return a list of sitelist objects the user is permitted to see."""

        s = models.SiteList.objects.all()

        return s


def site_subselect(request, sites):
    """Return a description and query subset, depending on GET variables.

    Consume a request object, queryset of Site model objects. Return a
    (group_name, sites) tuple where:

        group_name is a string contining the search field and value.

        sites is a queryset of Site objects answering any GET requests
        in the request.

    """

    group_name = ""

    if 'site_type' in request.GET:
        request.session['site_type'] = request.GET['site_type']
        sites = sites.filter(site_type__iexact=request.GET['site_type'])
        group_name = 'Site type: ' + request.GET['site_type']

    if 'site_subtype' in request.GET:
        request.session['site_subtype'] = request.GET['site_subtype']
        sites = sites.filter(site_subtype__iexact=request.GET['site_subtype'])
        group_name = 'Site subtype: ' + request.GET['site_subtype']

    if 'lgcy_type' in request.GET:
        request.session['lgcy_type'] = request.GET['lgcy_type']
        sites = sites.filter(lgcy_type__iexact=request.GET['lgcy_type'])
        group_name = 'Site type (from ArchSite): ' + request.GET['lgcy_type']

    if 'quality' in request.GET:
        quality = request.GET['quality']
        if quality.lower() == 'none':
            quality = None
        sites = sites.filter(record_quality__iexact=quality)
        group_name = ". Record quality: " + str(quality)

    if 'recorded_by' in request.GET:
        recorded_by = request.GET['recorded_by']
        if recorded_by.lower() == 'none':
            recorded_by = None
        sites = sites.filter(recorded_by__icontains=recorded_by)
        group_name = ". Recorded by contains: " + str(recorded_by)

    # UNFINISHED. Need a Q lookup, I think.
    if 'affected_by' in request.GET:
        affected_by = request.GET['affected_by']
        group_name = ". Affected by contains: " + str(recorded_by)

    return (group_name, sites)
