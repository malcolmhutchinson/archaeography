"""Archaeography models for the NZAA application.

This application models archaeological site records, and the process
of providing updated information to them.

It centres around the Site class, which contains aggregate fields for
searching and sorting. The descriptive data are held in update records
attached to sites. Each site record should have an update-0 attached
to it. This will contain a copy of the ArchSite record.

The aggregate fields are common between site and update tables, and
have therefore been specified in the abstract model `Record`.

Ancilliary tables are also specified here, modelling the file
attachments to a site record. There is also a SiteList model, which
allows for the compilation of lists of site records of arbitrary
length and composition.

"""

from __future__ import unicode_literals
import os
import re
import datetime
from textwrap import TextWrapper, wrap
import pytz
from markdown2 import markdown

from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from django.contrib.auth.models import User
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

import settings
import geolib

import webnote
import webnote.settings
import utils


UPDATE_TYPE = (
    ('Comment', 'Comment'),
    ('Request for deletion', 'Request for deletion'),
    ('Archaeological investigation', 'Archaeological investigation'),
    ('Historical information', 'Historical information'),
    ('Reclassify or move', 'Reclassify or move'),
    ('Remote sensing', 'Remote sensing'),
    ('Site visit', 'Site visit'),
    ('Legacy', 'Legacy'),
)

OPSTATUS = (
    ('Working', 'Working'),
    ('Staging', 'Staging'),
    ('Standing', 'Standing'),
    ('Completed', 'Completed'),
    ('Hold', 'Hold'),
)

STATUS = (
    (None, '-'),
    ('Pending', 'Pending'),
    ('Submitted', 'Submitted'),
    ('Returned', 'Returned'),
    ('Accepted', 'Accepted'),
    ('Approved', 'Approved'),
)


class Record(models.Model):
    """Superclass for the site and update classes.

    Provide overloaded methods for saving records with appropriate
    logging. Also provide common fields between site and update
    classes.

    Abstract class, no database table called record.
    """

    store_unref_figs = None
    store_long_fields = None

    class Meta:
        abstract = True

    SITE_TYPE = settings.get_choices(settings.SITE_TYPE, sort=True)
    SITE_SUBTYPE = settings.get_site_subtype()
    PERIOD = settings.get_choices(settings.PERIOD)
    ETHNICITY = settings.get_choices(settings.ETHNICITY)
    REGION = settings.get_choices(settings.REGION)

    RE_NZAA_ID = r'[A-Za-z]\d{2}/\d+'
    RE_TEMP_ID = r'[A-Z]{1,3}/\d+'
    RE_TOPO50_ID = r'[ABC][A-Z]d{2}/\d+'

    ordinal = models.PositiveIntegerField(editable=False)

    site_name = models.CharField(
        max_length=255, verbose_name='Site name',
        blank=True, null=True)

    other_name = models.CharField(
        max_length=255, verbose_name='Other name',
        blank=True, null=True)

    site_type = models.CharField(
        blank=True, null=True, max_length=255, choices=SITE_TYPE,
    )

    site_subtype = models.CharField(
        verbose_name='Subtype', choices=SITE_SUBTYPE,
        max_length=255, blank=True, null=True)

    location = models.CharField(max_length=255, blank=True, null=True)

    period = models.CharField(
        max_length=255, choices=PERIOD, blank=True, null=True)

    ethnicity = models.CharField(
        max_length=255, choices=ETHNICITY, blank=True, null=True)

    landuse = models.CharField(max_length=255, blank=True, null=True)
    threats = models.CharField(max_length=255, blank=True, null=True)

    features = models.CharField(
        max_length=2048, blank=True, null=True,
    )

    associated_sites = models.CharField(
        max_length=2048, blank=True, null=True
    )

    visited = models.DateField(
        verbose_name='Visited (date)', blank=True, null=True)

    visited_by = models.CharField(max_length=255, blank=True, null=True)

    easting = models.PositiveIntegerField()
    northing = models.PositiveIntegerField()
    radius = models.IntegerField(default=0, blank=True, null=True)

    geom = models.PointField(srid=2193, blank=True, null=True)
    geom_poly = models.MultiPolygonField(srid=2193, blank=True, null=True)

#   Common metadata fields.
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name='Record created at')

    created_by = models.CharField(
        max_length=255, editable=False, verbose_name='Record created by')

    modified = models.DateTimeField(
        null=True, blank=True, auto_now=True,
        editable=False, verbose_name='Record modified at')

    modified_by = models.CharField(
        max_length=255, null=True, blank=True,
        editable=False, verbose_name='Record modified by')

    accessioned = models.DateTimeField(
        verbose_name='Accessioned on', editable=False, blank=True, null=True)

    accessioned_by = models.CharField(
        max_length=255, verbose_name='Accessioned by',
        editable=False, blank=True, null=True)

    provenance = models.TextField(
        editable=False, verbose_name='Record provenance')

    extracted = models.DateTimeField(editable=False, blank=True, null=True)

    log = models.TextField(editable=False)

#   Record-level authorisation.
    owner = models.CharField(max_length=255, blank=True, null=True)
    edit = models.CharField(max_length=255, blank=True, null=True)
    allow = models.CharField(max_length=255, blank=True, null=True)
    deny = models.CharField(max_length=255, blank=True, null=True)

    notifications = []

    def save(self, log=None, *args, **kwargs):
        """Overide save() to provide logging facilities."""

        now = datetime.datetime.now(pytz.timezone('NZ'))
        timestamp = unicode(now.replace(microsecond=0))
        ipno = '127.0.0.1'
        user = 'machine'
        comment = 'Saving from unlogged command.'

        self.geom = Point(int(self.easting), int(self.northing), srid=2193)

        if not os.path.isdir(self.filespace_path()):
            os.makedirs(self.filespace_path())

        if log:
            ipno = log[0]
            user = log[1]
            comment = log[2]

        self.geom = Point(int(self.easting), int(self.northing), srid=2193)

        if not os.path.isdir(self.filespace_path()):
            os.makedirs(self.filespace_path())

        line = '\t'.join((timestamp, ipno, str(user), comment)) + '\n'
        self.log += line

        if hasattr(self, 'update_id') and self.update_id is not None:
            identifier = self.update_id
        elif hasattr(self, 'newsite_id'):
            identifier = self.newsite_id
        else:
            identifier = self.nzaa_id

        filename = identifier.replace('/', '-') + '.log'
        logdir = os.path.join(self.filespace_path(), 'etc')
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        logfile = os.path.join(self.filespace_path(), 'etc', filename)

        f = open(logfile, 'a')
        f.write(line)
        f.close()

        super(Record, self).save(*args, **kwargs)

    def airphotos(self):
        """List the objects in geolb.AerialFrame intersecting with this object.

        """
        return geolib.models.AerialFrame.objects.filter(
            geom__intersects=self.geom)

    def archsite_url(self):
        return settings.SITE_PAGE + self.nzaa_id

    def clean_log(self):
        """Remove IP numbers from log streams. """

        log = self.log
        clean_log = []
        p = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\t')

        for line in log.split('\n'):
            clean_log.append(p.sub('', line))

        return '\n'.join(clean_log)

    def closest_placenames(self):
        """Return a list (placename, distance(m)) tuples of the closest places.

        Return the three closest named places to this site.

        """

        n = 3
        i1 = geolib.models.PlaceName.objects.filter(
            geom__distance_lte=(self.geom, D(m=10000)))
        i2 = i1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

        places = []

        for i in range(0, n):
            line = (i2[i].name, self.geom.distance(i2[i].geom))
            places.append(line)

        return places

    def closest_road(self):
        """Return a (name, distance) tuple for the road line closest.

        """

        i1 = geolib.models.Topo50_Road.objects.filter(
            geom__distance_lte=(self.geom, D(m=10000)))
        i2 = i1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

        if len(i2) > 0:
            name = i2[0].name
            distance = self.geom.distance(i2[0].geom)

            return name, distance

        return None

    def closest_sites(self):
        """Return (nzaa_id, distance) for the n closest sites to this site. """

        n = 3 + 1
        i1 = Site.objects.filter(
            geom__distance_lte=(self.geom, D(m=100000)))
        i2 = i1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

        if len(i2) < n:
            n = len(i2)

        sites = []

        for i in range(0, n):
            if not i2[i].nzaa_id == self.nzaa_id:
                line = (i2[i].nzaa_id, self.geom.distance(i2[i].geom))
                sites.append(line)

        return sites

    def display_assoc_sites(self):
        return self.associated_sites

    def display_condition(self):
        return markdown(self.condition)

    def display_created(self):
        created = self.created.strftime("%Y-%m-%d %M:%S")
        created += " by user " + self.created_by
        return created

    def display_description(self):
        return markdown(self.descrption)

    def display_finder_aid(self):
        return markdown(self.finder_aid)

    def display_introduction(self):
        return markdown(self.introduction)

    def display_modified(self):
        modified = self.modified.strftime("%Y-%m-%d %M:%S")
        modified += " by user " + self.created_by
        return modified

    def display_references(self):
        return markdows(self.reference)

    def display_rights(self):
        return markdown(self.rights)

    def display_site_type(self):
        display_type = self.site_type
        if self.site_subtype:
            display_type += '/ ' + self.site_subtype

        return display_type

    def display_visited(self):
        visited = 'No data'

        if not self.visited and not self.visited_by:
            return "No data"

        if self.visited_by == 'Not known' or self.visited_by == 'Unknown':
            if self.visited:
                return "Unknown after " + str(self.visited)
            return "Unknown"

        if self.visited_by == 'Not visited':
            return "Not visited"

        if self.visited:
            visited = str(self.visited)
        if self.visited_by:
            visited += " by " + self.visited_by

        return visited

    def distance_to_coast(self):
        if self.dist_to_coast:
            return self.dist_to_coast

        c = geolib.models.Waterways.objects.filter(type_name='Coastline')
        c1 = c.filter(geom__distance_lte=(self.geom, D(m=1000000)))

        c2 = c1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

    def _footprint(self):
        return self.geom_poly

    footprint = property(_footprint)

    def _nzmg_coords(self):
        """Return a display string containing coords.

        Finding a grid reference

        The coord conversion yields a one-digit error. That is, a
        number may be come out to 100006, for example. This was a
        common enough occurrance to need some sort of solution.

        That solution was to truncate the last digit, then find the
        modulus of 10.

        """

        p = Point(self.geom.x, self.geom.y, srid=2193)
        p.transform(27200)
        x = str(int(p.x))[:-1]
        y = str(int(p.y) + 1)[:-1]

        # This is weird. Why are we talking about distances to the coasts?
        if len(c2):
            self.dist_to_coast = int(c2[0].distance.m)
            return self.dist_to_coast

    # Won't work without data in coasts and waterways.
    def distance_to_coast_str(self):
        if not self.dist_to_coast:
            self.waterways()

        d = self.distance_to_coast()

        if d > 1000:
            return str(d / 1000) + ' km'
        return str(d) + ' m'

    # Won't work without data in coasts and waterways.
    def distance_to_water(self):
        w = geolib.models.Waterways.objects.all()
        w1 = w.filter(geom__distance_lte=(self.geom, D(m=1000000)))
        w2 = w1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

        if len(w2):
            return int(w2[0].distance.m)

    def footprint(self):
        return self.geom_poly

    def get_aerialframes(self):
        """Historic photos on which this site may be visible.

        Return a list of tuples containing:

            (AerialFrame object, distance from centroid)

        This is purely for easy listing in a template. The closer to
        the centre of the frame, the better this site will be visible
        in it.

        """

        if not self.geom:
            return None

        output = []
        queryset = geolib.models.AerialFrame.objects.filter(
            geom__intersects=self.geom)

        for frame in queryset:
            c = frame.geom.centroid
            dist = self.geom.distance(c)
            output.append((frame, dist))

        return output

    def get_easting(self):
        return int(self.geom.coords[0])

    def get_island(self):
        """Return a string the name of the island the site falls in, or
        closest to.

        """

        try:
            i = geolib.models.Topo50_Island.objects.get(
                geom__intersects=self.geom)
            return i.name
        except geolib.models.Topo50_Island.DoesNotExist:
            i = geolib.models.Topo50_Island.objects.all()
            i1 = i.filter(geom__distance_lte=(self.geom, D(m=10000)))
            i2 = i1.annotate(
                distance=Distance('geom', self.geom)).order_by('distance')

            if len(i2):
                return i2[0].name

        return None

    def get_northing(self):
        return int(self.geom.coords[1])

    def get_nzms_sheet(self):
        """Return the NZMS260 map object the site is found on."""

        r = geolib.models.TopoMap.objects.filter(
            series_id='NZMS260', geom__intersects=self.geom)
        if r.count():
            return r[0]

        try:
            r = geolib.models.NZMSgrid.objects.get(geom__intersects=self.geom)
            return r
        except geolib.models.NZMSgrid.DoesNotExist:
            return None

    def get_point_parcel(self):
        """Return the cadastral parcel the point location intersects with.
        """

        try:
            p = geolib.models.Cadastre.objects.get(geom__intersects=self.geom)
            return p
        except geolib.models.Cadastre.DoesNotExist:
            return None

    def get_parcels(self):
        """Return a queryset of parcels intersecting with the footprint.

        """

        if not self.footprint:
            self.geom_poly = self.compute_footprint()

        p = geolib.models.Cadastre.objects.filter(
            geom__intersects=self.geom_poly)

        return p

    def get_region(self):
        """Return the name of the region the site is found in."""

        try:
            r = geolib.models.Region.objects.get(geom__intersects=self.geom)
            return r.name
        except geolib.models.Region.DoesNotExist:
            t = geolib.models.Region.objects.all()
            t1 = t.filter(geom__distance_lte=(self.geom, D(m=10000)))
            t2 = t1.annotate(
                distance=Distance('geom', self.geom)).order_by('distance')

            if len(t2):
                return t2[0].name

    def get_tla(self):
        """Return the name of the territorial authority the site is in."""

        try:
            ta = geolib.models.TerritorialAuthority.objects.get(
                geom__intersects=self.geom)
            return ta.name
        except geolib.models.TerritorialAuthority.DoesNotExist:

            t = geolib.models.TerritorialAuthority.objects.all()
            t1 = t.filter(geom__distance_lte=(self.geom, D(m=10000)))
            t2 = t1.annotate(
                distance=Distance('geom', self.geom)).order_by('distance')

            if len(t2):
                return t2[0].name

    def get_topo50_sheet(self):
        """Return the Topo map object the site is found on.

        This is from a geographic calculation, not from the nzaa_id.
        """

        r = geolib.models.TopoMap.objects.filter(
            series_id='TOPO50', geom__intersects=self.geom)
        return r[0]

    def legacy_coords(self):
        return str(self.lgcy_easting) + " " + str(self.lgcy_northing)

    def latitude(self):
        p = Point(self.geom.x, self.geom.y, srid=2193)
        p.transform(4326)
        return p.y

    def lidar_tiles(self):
        """List the objects from IndesLidar intersecting with this object.

        """
        return geolib.models.IndexLidar.objects.filter(
            geom__intersects=self.geom)

    def link_site_ids(self, text):
        """Return the text, with NZAA identifiers encased in HTML anchors.
        """
        ex = self.RE_NZAA_ID
        ex = r'([A-Za-z]\d{2}/\d+)'
        p = re.compile(ex)
        m = p.findall(text)

        for match in m:
            link = (
                "<a href='/nzaa/" + match + "'>" +
                match + "</a>"
            )
            text = text.replace(
                match, "<a href='/nzaa/" + match + "'>" + match + "</a>")

        ex = self.RE_TEMP_ID
        ex = r'[A-Z]{1,3}/\d+'
        p = re.compile(ex)
        m = p.findall(text)

        for match in m:
            text = text.replace(
                match, "<a href='/nzaa/" + match + "'>" + match + "</a>")

        return text

    def list_actors(self):
        """Return a list of unique values that are names.

        Names appear in the _by fields; visited_by is often populated
        from an Archsite record. These are semi-colon separated.

        """

        p = Point(self.geom.x, self.geom.y, srid=2193)
        p.transform(27200)
        x = str(int(p.x))[:-1]
        y = str(int(p.y) + 1)[:-1]

        sourcenames = []
        if self.visited_by:
            names = self.visited_by.split(';')
            for name in names:
                sourcenames.append(name.strip())

        if self.recorded_by:
            names = self.recorded_by.split(';')
            for name in names:
                sourcenames.append(name.strip())

        if self.updated_by:
            names = self.updated_by.split(';')
            for name in names:
                sourcenames.append(name.strip())

        sourcenames = set(sourcenames)
        return list(sourcenames)

    def list_features(self):
        """Return a list of unique values from the features field.

        We trap only incoming data, from the legacy field. Values in
        the 'period' field will be interpreted from thin incoming
        values, into a controlled vocabulary.

        """

        feats = []
        if self.features:
            bits = self.features.split(',')
            for bit in bits:
                if bit.strip() not in feats:
                    feats.append(bit.strip())

            return feats

    def list_periods(self):
        """Return a list of unique values from the period field.

        We trap only incoming data, from the legacy field. Values in
        the 'period' field will be interpreted from thin incoming
        values, into a controlled vocabulary.

        """

        periods = []
        bits = self.lgcy_period.split(',')
        for bit in bits:
            if bit.strip() not in periods:
                periods.append(bit.strip())

        return periods

    def long_fields_text(self):

        text = ""

        if self.introduction:
            text += "### Introduction\n\n"
            wtext = w.wrap(self.introduction)
            for i in wtext:
                text += '\n' + i

        if self.finder_aid:
            text += "### Full finder aid\n\n"
            text += self.wrap_field(self.finder_aid)

        if self.description:
            text += "### Site description\n\n"
            text += self.wrap_field(self.description)

        if self.condition:
            text += "### Statement of condition\n\n"
            text += self.wrap_field(self.condition)

        if self.references:
            text += "### References\n\n"
            text += self.wrap_field(self.references)

        if self.rights:
            text += "### Rights\n\n"
            text += self.wrap_field(self.rights)

        return text

    def long_fields(self):
        """Provide one string containing long text fields.

        Parse the introduction, finder aid, description an condition
        statement into a single markdown string.

        This is supposed to convert nzaa identifiers to record links,
        but that bit doesn't work properly yet.

        """

        if self.store_long_fields:
            return self.store_long_fields

        text = ''

        if self.introduction:
            text += "### Introduction\n\n"
            text += self.introduction + '\n\n\n'

        if self.finder_aid:
            text += "### Full finder aid\n\n"
            text += self.finder_aid + '\n\n\n'

        if self.description:
            text += "### Site description\n\n"
            text += self.description + '\n\n\n'

        if self.condition:
            text += "### Statement of condition\n\n"
            text += self.condition + '\n\n\n'

        if self.references:
            text += "### References\n\n"
            text += self.references + '\n\n\n'

        if self.rights:
            text += "### Rights\n\n"
            text += self.rights + '\n\n\n'

        # This changes state, setting global attributes.
        if self.filespace():
            result, unref = self.filespace().reference_text(text)
            self.store_long_fields = markdown(result)
            self.store_unref_figs = unref

        else:
            self.store_long_fields = markdown(text)
            self.store_unref_figs = []

        return self.store_long_fields

    def longitude(self):
        p = Point(self.geom.x, self.geom.y, srid=2193)
        p.transform(4326)
        return p.x

    def mapfile(self):
        """Return a dictionary structure cpntaining variables for a mapfile.

        """

        xmin = self.easting - 2000
        xmax = self.easting + 2000
        ymin = self.northing - 2000
        ymax = self.northing + 2000

        extent = str(xmin) + ' ' + str(ymin) + ' '
        extent += str(xmax) + ' ' + str(ymax)

        projection = """"proj=tmerc"
      "lat_0=0"
      "lon_0=173"
      "k=0.9996"
      "x_0=1600000"
      "y_0=10000000"
      "ellps=GRS80"
      "towgs84=0,0,0,0,0,0,0"
      "units=m"
      "no_defs" """

        mapfile = {
            'size_x': 1024,
            'size_y': 820,
            'extent': extent,
            'projection': projection,
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax,
            'username': settings.MACHINE[0],
            'password': settings.MACHINE[1],
        }

        return mapfile

    def mapsheets(self):
        """List the objects from MapIndex intersecting with this object.

        """
        return geolib.models.TopoMap.objects.filter(
            geom__intersects=self.geom)

    def nzmg_coords(self):
        """Return a display string containing coords.

        Finding a grid reference

        The coord conversion yields a one-digit error. That is, a
        number may be come out to 100006, for example. This was a
        common enough occurrance to need some sort of solution.

        That solution was to truncate the last digit, then find the
        modulus of 10.

        """

        p = Point(self.geom.x, self.geom.y, srid=2193)
        p.transform(27200)
        x = str(int(p.x))[:-1]
        y = str(int(p.y) + 1)[:-1]

        if int(x) % 10 == 0 and int(y) % 10 == 0:
            x = str(int(p.x))[2:-2]
            y = str(int(p.y))[2:-2]
            return "NZMG Grid ref " + x + " " + y

        return str(int(p.x)) + " " + str(int(p.y))

    def nzmg_gridref(self):
        """Return True if the geometry resolves to a grid reference.

        A grid reference is given as eastings and northings to
        100m. Convention has it that this number identifies the south
        west corner of a 100m square.

        This is found by converting the NZTM eastings and northings
        back to NZMG, and testing for divisibility by 100.

        """
        p = Point(self.geom.x, self.geom.y, srid=2193)
        p.transform(27200)

        x = str(int(p.x))[:-1]
        y = str(int(p.y) + 1)[:-1]

        if int(x) % 10 == 0 and int(y) % 10 == 0:
            return True

        return False

    def nztm_coords(self):
        coords = str(self.easting) + ' ' + str(self.northing)
        return coords

    def ortho_tiles(self):
        """List the objects from IndexOrtho intersecting with this object.

        """
        return geolib.models.OrthoTile.objects.filter(
            geom__intersects=self.geom)

    def parcels(self):
        """Return the cadastral parcels this site sits in."""

        return geolib.models.Cadastre.objects.filter(
            geom__intersects=self.geom)

    def primary_coast(self):
        c = geolib.models.Waterways.objects.filter(type_name='Coastline')
        c1 = c.filter(geom__distance_lte=(self.geom, D(m=1000000)))
        c2 = c1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

        if len(c2):
            return c2[0].base_name

    def primary_waterway(self):
        w = geolib.models.Waterways.objects.all()
        w1 = w.filter(geom__distance_lte=(self.geom, D(m=10000)))

        if w1:

            w2 = w1.annotate(
                distance=Distance('geom', self.geom)).order_by('distance')
            if len(w2):
                return w2[0].base_name
        else:
            return "Unknown"

    # This needs reworking to accommodate the Topo50 names in new records.
    def replace_temp_ids(self, text):
        """Search the text fields for references to new records.

        For each instance of a new record reference, check the new
        record, to see if there is an NZAA id for the record
        (indicating it has been accessioned into the collection).

        """

        text = "Not done yet"
        return text

    def update_actors(self):
        """Change the actors table as appropriate."""

        for actor in self.list_actors():
            try:
                a = Actor.objects.get(sourcename=actor)
                print "Found actor record for", actor
            except Actor.DoesNotExist:
                print "Creating actor record for ", actor
                a = Actor(sourcename=actor)
                a.save()

            a.sites.add(sites=self)

    def unref_figs(self):
        if self.store_unref_figs:
            return self.store_unref_figs

        long_fields = self.long_fields()
        return self.store_unref_figs

    def wrap_field(self, field):

        result = ""
        w = TextWrapper()
        txt = field.replace("\n \n", "\n\n")
        pars = txt.split('\n\n')

        for p in pars:
            newpar = ''
            lines = w.wrap(p)
            for l in lines:
                newpar += l + '\n'
            result += newpar + '\n\n'

        return result

    def wgs_coords(self):
        return "Lat/lon " + str(self.latitude()) + " " + str(self.longitude())


class Site(Record):
    """Everything about an archaeological site.

    This model holds all fields, stored and computed, for a site
    record. Fields are broadly divided into data fields and aggregate
    fields. The first holds the archaeolgical information and the
    second holds values for searching and sorting.

    Database fields described here are aggregate fields. We compute
    values for locations (territorial authorities, regions and
    islands) and store them, so searches on those groups are faster.

    We also store legacy values, which are those copied directly from
    ArchSite. These will be updated when scrape is run.

    """

    TLA = settings.get_choices(settings.TLA)
    REGION = settings.get_choices(settings.REGION)

    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
    )

    RECORD_QUALITY = (
        ('trivial', 'trivial'),
        ('sparse', 'sparse'),
        ('thin', 'thin'),
        ('adequate', 'adequate'),
        ('comprehensive', 'comprehensive'),
        ('missing', 'missing'),
    )

    update_id = None
    updateRecords = None

    dist_to_coast = 0
    nearest_coast = None
    dist_to_water = 0
    nearest_waterway = None

#   Identifiers and locators.
    nzaa_id = models.CharField(
        max_length=10, verbose_name='NZAA id', primary_key=True)

    nzms_id = models.CharField(
        max_length=10, verbose_name='NZMS id', blank=True, null=True,
        help_text='Imperial ID for older site records.')

    nzms_sheet = models.CharField(max_length=10, editable=False)

    tla = models.TextField(
        verbose_name='Territorial authority',
        choices=TLA, blank=True, null=True)

    region = models.CharField(
        max_length=255, verbose_name='Region',
        choices=REGION, blank=True, null=True)

    island = models.TextField(
        verbose_name='Island', blank=True, null=True)

#   Record metadata
    record_quality = models.CharField(
        max_length=255, choices=RECORD_QUALITY,
        blank=True, null=True)

    assessed = models.DateTimeField(
        blank=True, null=True,
        auto_now=True, editable=False,
        verbose_name='Record assessed at'
    )

    assessed_by = models.CharField(
        max_length=255, blank=True, null=True,
        editable=False, verbose_name='Record assessed by'
    )

#   Legacy fields.
    lgcy_assocsites = models.TextField(
        verbose_name='Associated sites',
        editable=False, blank=True, null=True)

    lgcy_capmethod = models.TextField(
        verbose_name='Capture method',
        editable=False, blank=True, null=True)

    lgcy_condition = models.TextField(
        verbose_name='Condition', editable=False, blank=True, null=True)

    lgcy_ethnicity = models.TextField(
        verbose_name='Ethnicity',
        editable=False, blank=True, null=True)

    lgcy_evidence = models.TextField(
        verbose_name='Evidence of destruction',
        editable=False,
        blank=True, null=True)

    lgcy_inspected = models.TextField(
        verbose_name='Inspected',
        editable=False, blank=True, null=True)

    lgcy_landuse = models.TextField(
        verbose_name='Land use',
        editable=False, blank=True, null=True)

    lgcy_period = models.TextField(
        verbose_name='Period',
        editable=False, blank=True, null=True)

    lgcy_shortdesc = models.TextField(
        verbose_name='Short description',
        editable=False, blank=True, null=True)

    lgcy_status = models.TextField(
        verbose_name='Status',
        editable=False, blank=True, null=True)

    lgcy_features = models.CharField(
        max_length=2048, blank=True, null=True,
    )

    lgcy_threats = models.TextField(
        verbose_name='Threats',
        editable=False, blank=True, null=True)

    lgcy_type = models.TextField(
        verbose_name='Site type',
        editable=False, blank=True, null=True)

    lgcy_easting = models.IntegerField(
        verbose_name='NZTM easting',
        editable=False, blank=True, null=True)

    lgcy_northing = models.IntegerField(
        verbose_name='NZTM northing',
        editable=False, blank=True, null=True)

#   Metadata fields.
    recorded = models.DateField(
        verbose_name='Date recorded', blank=True, null=True)

    recorded_by = models.TextField(
        blank=True, null=True, verbose_name='Site recorded by')

    updated = models.DateField(
        blank=True, null=True, verbose_name='Site last updated on')

    updated_by = models.CharField(
        max_length=255,
        blank=True, null=True, verbose_name='Site last updated by')

    status = models.TextField(
        max_length=255, choices=STATUS, blank=True, null=True)

#   MD5 digest of scraped values. See scrape.Scrape.extract_values.
    digest = models.CharField(
        editable=False, max_length=255, blank=True, null=True
    )
    last_change = models.DateTimeField(editable=False, blank=True, null=True)

    class Meta:
        ordering = ['nzms_sheet', 'ordinal']
        get_latest_by = 'recorded'

    def __unicode__(self):
        return self.nzaa_id

    def get_absolute_url(self):
        return os.path.join(settings.BASE_URL, self.nzaa_id)

    url = property(get_absolute_url)

    def all_documents(self):
        return Document.objects.filter(update__site=self)

    def breadcrumbs(self):
        """Return a list of tuples which can be appended to any link list.
        """

        if self.updates.all().count() > 1:
            return True

        return False

    def compute_footprint(self):
        """Return a polygon geometry describing the extent of the site.

        If the MZTM coords resolve to an NZMS260 grid reference (of
        six digits), then the geometry is a square, 100 m on a side,
        with the south west corner sitting on the coords.

        Otherwise, the geometry is a circle 50 m, centred on the
        coords.

        """

    def count_files(self):
        """Number of files in a filespace."""

        count = 0
        for update in self.updates.all():
            count += update.count_files()

        return count

    def display_associated_sites(self):
        sites = self.replace_temp_ids(self.associated_sites)
        sites = self.link_site_ids(sites)
        return sites

    def display_short_description(self):
        """Replace the superclass description with this method.

        """

        u = self.updates().filter(opstatus=None)
        u = u.exclude(description=None).exclude(description='')
        if u.count() > 0:
            desc = u[0].display_description().split('\n\n')
            return desc[0]

        return self.short_description

    def short_description_txt(self):

        result = ''
        u = self.updates().filter(opstatus=None)
        u = u.exclude(description=None).exclude(description='')
        if u.count() > 0:
            desc = u[0].description.split('\n\n')
            text = desc[0]

        else:
            text = self.short_description

        lines = wrap(text)
        for l in lines:
            result += l + '\n'

        return result

    def display_finder_aid(self):
        """Replace the superclass description with this method.

        """

        u = self.updates().filter(opstatus=None)
        u = u.exclude(finder_aid=None).exclude(finder_aid='')
        if u.count() > 0:
            return markdown(u[0].finder_aid)

        return None

    def display_recorded(self):
        if not self.recorded and not self.recorded_by:
            return "No data"

        recorded = ''
        if self.recorded:
            recorded += str(self.recorded)
        if self.recorded_by:
            recorded += ' by ' + self.recorded_by
        else:
            recorded += " by an unknown researcher."

        return recorded

    def display_record_quality(self):
        quality = self.record_quality
        if not quality:
            quality = "Not known"
        return quality

    def display_updated(self):
        updated = 'No data'

        if not self.updated and not self.updated_by:
            return "No data"

        if self.updated_by == 'Not updated':
            return "Not updated"

        if self.recorded == self.updated:
            return "Not updated"

        if self.updated_by == 'Not known' or self.updated_by == 'Unknown':
            if self.updated:
                return "Unknown after " + str(self.updated)
            return "Unknown"

        if self.updated:
            updated = str(self.updated)
        if self.updated_by:
            updated += " by " + self.updated_by

        return updated

    def display_updates(self):
        return self.updates().filter(opstatus=None)

    def filespace_path(self):
        """Return a string filepath to the object's filespace.

        The filespace for an object is the BASE_FILESPACE setting,
        with the nzaa_id appended.

        If the nzaa_id and the temp_id are the same, meaning this
        record has a temporary identifier, then the filespace is in
        the tmp directory.
        """

        return os.path.join(settings.BASE_FILESPACE, self.nzaa_id)

    def filespace(self):
        """Return a webnote Directory object for this record.

        """

        path = self.filespace_path()
        docroot = ''
        baseurl = ''
        try:
            d = webnote.Directory(path, docroot, baseurl)

        except webnote.Directory.ParseDirNotFound:
            return None

        return d

    def get_siteLists(self):
        """return a queryset of sitelist objects this site belongs to.
        """
        return self.sitelist_set.all()

    def latest_review(self):
        """Return one review record, the latest for this site record.
        """

        return self.review.all().order_by('-reviewed')[0]

    def lgcy_coords(self):
        coords = "NZTM "
        coords += str(self.lgcy_easting) + ' ' + str(self.lgcy_northing)
        return coords

    def next_update(self):
        """Return an integer ordinal for the next update record."""
        return self.updates[0].ordinal + 1

    def old_values(self):
        """Return a dictionary which can be used to populate a review object.

        """
        old_values = {

            'from_site_name': self.site_name,
            'from_site_type': self.site_type,
            'from_site_subtype': self.site_subtype,
            'from_location': self.location,
            'from_recorded_by': self.recorded_by,
            'from_updated_by': self.updated_by,
            'from_visited_by': self.visited_by,
            'from_recorded': self.recorded,
            'from_visited': self.visited,
            'from_updated': self.updated,
            'from_site_type': self.site_type,
            'from_site_subtype': self.site_subtype,
            'from_period': self.period,
            'from_ethnicity': self.ethnicity,
            'from_record_quality': self.record_quality,
        }
        return old_values

    def pending_updates(self):
        """Return a queryset of updates with opstatus != None."""
        return self.updates().exclude(opstatus=None)

    def set_update(self, update_id):
        self.updateRecords = Update.objects.filter(update_id=update_id)

    def short_description(self):

        if self.updates[0].ordinal == 0:
            return self.lgcy_shortdesc

        description = ''

#       Splitting by paragraphs may give unexpected reslts.
        if self.updates[0].description:
            paras = self.updates[0].description.split('\r\n\r\n')
            if len(paras) > 0:
                return paras[0]

        return self.lgcy_shortdesc

    def title(self):
        """Compute a string value for the site title.

        The site title contains the site name and the nzaa_id in
        parentheses. If there is no site name, the site type is used
        instead.

        The exception to this rule is sites of type 'pa'. These will
        be called "Unnamed pa (nzaa_id)".
        """

        title = ''
        site_id = '(' + self.nzaa_id + ')'
        if self.site_name:
            title = self.site_name + " " + site_id
        elif self.site_type.lower() == 'pa' or self.site_type.lower() == 'paa':
            title = 'Unnamed paa ' + site_id
        elif self.site_type:
            title = self.site_type + ' ' + site_id
        else:
            title = self.nzaa_id

        if self.nzms_id:
            title += " [" + self.nzms_id + "]"

        return title

    def update0(self):
        """Return the single update record update0 (the ArchSite copy). """

        return self.updates().get(ordinal=0)

    def updates(self, update_id=None):

        if not self.updateRecords:
            self.updateRecords = Update.objects.filter(site=self)

        return self.updateRecords

    def updates_count(self):
        """Counts non-zero updates."""
        return self.updates.filter(ordinal__gte=1).count()


class NewSite(Record):
    """Records for peviously unrecorded archaeolgical sites.


    Kept separate from the Site table so as to avoid confusing the
    count.

    """

    BASE_FILESPACE = os.path.join(settings.BASE_FILESPACE, 'newsites')

    newsite_id = models.CharField(max_length=16, primary_key=True)
    field_id = models.CharField(max_length=255, blank=True, null=True)
    field_notes = models.TextField(blank=True, null=True)
    recorded = models.DateField()
    recorded_by = models.CharField(max_length=255)
    topo50_sheet = models.CharField(max_length=255, blank=True, null=True)

    update_type = models.CharField(max_length=255, choices=UPDATE_TYPE)

    introduction = models.TextField(blank=True, null=True)

    finder_aid = models.TextField(
        verbose_name='Aid to relocation', blank=True, null=True)

    description = models.TextField(
        verbose_name='Description', blank=True, null=True)

    condition = models.TextField(
        verbose_name='Condition statement', blank=True, null=True)

    references = models.TextField(
        verbose_name='References', blank=True, null=True)

    rights = models.TextField(blank=True, null=True)

    status = models.TextField(
        choices=settings.get_choices(settings.STATUS),
        blank=True, null=True)

    opstatus = models.CharField(
        max_length=255, verbose_name='status',
        choices=OPSTATUS,
        blank=True, null=True
    )

    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        ordering = ['topo50_sheet', 'ordinal']
        get_latest_by = 'recorded'

    def __unicode__(self):
        return self.newsite_id

    def display_recorded(self):
        if not self.recorded and not self.recorded_by:
            return "No data"

        recorded = ''
        if self.recorded:
            recorded += str(self.recorded)
        if self.recorded_by:
            recorded += ' by ' + self.recorded_by
        else:
            recorded += " by an unknown researcher."

        return recorded

    def get_absolute_url(self):
        return os.path.join(settings.BASE_URL, self.newsite_id)

    url = property(get_absolute_url)

    def filespace_path(self):
        """Return a string containing the filesystem path to the filespace.
        """

        return os.path.join(self.BASE_FILESPACE, self.newsite_id)

    def filespace(self):
        """Return a webnote Dictionary object.
        """

        path = self.filespace_path()
        docroot = ''
        baseurl = ''

        path = self.filespace_path()
        docroot = self.url.replace('-', '/')
        baseurl = os.path.join('/static/', docroot[1:].replace(
            'nzaa/', 'nzaa/newsites/'))

        try:
            d = webnote.Directory(path, docroot, baseurl)

        except webnote.Directory.ParseDirNotFound:
            return None

        return d

    def get_nzaa_id(self):
        """Calculate what would be the current NZAA id.

        Make sure the NZMZ260 sheet set has been scraped, if you want
        an accurate prediction against ArchSite.
        """

        nzms260_sheet = geolib.models.NZMSgrid.objects.filter(
            geom__intersects=self.geom)
        sites = Site.objects.filter(
            nzms_sheet=nzms260_sheet).order_by('-ordinal')
        ordinal = sites[0].ordinal + 1

        return nzms260_sheet.identifier + '/' + str(ordinal)

    def legacy_coords():
        """A placeholder, used with certain site templates."""

        return None

    def topo50_id(self):
        """Compute this new record's temporary id.

        A temp_id is based on the NZ Topo50 map grid. Each new site
        record within a given grid area is given an incrimenting
        integer, similar to the manner the NZAA id is computed.

        Examples: BB33/5.

        """

        topo50_sheet = geolib.models.Topo50grid.objects.filter(
            geom__intersects=self.geom
        )
        sites = Site.objects.filter(
            geom__intersects=self.geom
        )
        ordinal = sites[-1].ordinal + 1

        return topo50_sheet.identifier + '/' + str(ordinal)

    def title(self):
        """Return a string title for the site record."""

        title = self.newsite_id

        if self.site_type:
            title = self.site_type + ' (' + self.newsite_id + ')'

        return title


class Actor(models.Model):
    """An actor is any person or organisation named in the files.

    sourcename     The name as it appears in a record.
    fullname       A way of associating sourcenames with individuals.

    """

    sites = models.ManyToManyField(Site)
    sourcename = models.CharField(max_length=1024)
    fullname = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['sourcename']

    def __unicode__(self):
        return self.sourcename

    def get_absolute_url(self):
        return os.path.join(settings.BASE_URL, 'actor', str(self.id))

    url = property(get_absolute_url)

    def get_sourcename(self):
        if self.sourcename:
            return self.sourcename
        return "None"


class Feature(models.Model):
    """Unique values from the features field, from ArchSite.

    """

    sites = models.ManyToManyField(Site)
    name = models.CharField(max_length=1024)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return os.path.join(settings.BASE_URL, 'feature', str(self.id))

    url = property(get_absolute_url)

    def get_name(self):
        if self.name:
            return self.name
        return "None"


class Periods(models.Model):
    """Unique values for the period field, from ArchSite.
    """

    sites = models.ManyToManyField(Site)
    name = models.CharField(max_length=1024)

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return os.path.join(settings.BASE_URL, 'period', str(self.id))

    url = property(get_absolute_url)

    def get_name(self):
        if self.name:
            return self.name
        return "None"


class SiteTypes(models.Model):
    """Unique values for the period field, from ArchSite.
    """

    sites = models.ManyToManyField(Site)
    typename = models.CharField(max_length=1024)

    class Meta:
        ordering = ['typename']

    def get_absolute_url(self):
        return os.path.join(settings.BASE_URL, 'period', str(self.id))

    url = property(get_absolute_url)

    def get_typename(self):
        if self.typename:
            return self.typenamename
        return "None"


class Update(Record):

    UPDATE_TYPE = (
        ('Comment', 'Comment'),
        ('Request for deletion', 'Request for deletion'),
        ('Archaeological investigation', 'Archaeological investigation'),
        ('Historical information', 'Historical information'),
        ('Reclassify or move', 'Reclassify or move'),
        ('Remote sensing', 'Remote sensing'),
        ('Site visit', 'Site visit'),
        ('Legacy', 'Legacy'),
    )

    update_id = models.CharField(
        max_length=20, verbose_name='Update id', primary_key=True)

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name='sites'
    )

    update_type = models.CharField(max_length=255, choices=UPDATE_TYPE)

    field_id = models.CharField(max_length=255, blank=True, null=True)

    field_notes = models.TextField(blank=True, null=True)

    introduction = models.TextField(blank=True, null=True)

    finder_aid = models.TextField(
        verbose_name='Aid to relocation', blank=True, null=True)

    description = models.TextField(
        verbose_name='Description', blank=True, null=True)

    condition = models.TextField(
        verbose_name='Condition statement', blank=True, null=True)

    references = models.TextField(
        verbose_name='References', blank=True, null=True)

    rights = models.TextField(blank=True, null=True)

    update_note = models.TextField(blank=True, null=True)

    nzmg_gridref = models.CharField(max_length=255, blank=True, null=True)

    updated = models.DateField(
        verbose_name='Updated on', blank=True, null=True)

    updated_by = models.TextField(
        verbose_name='Updated by', blank=True, null=True)

    submitted = models.DateTimeField(
        editable=False, blank=True, null=True)

    submitted_by = models.TextField(
        editable=False, blank=True, null=True)

    uploaded = models.DateTimeField(
        editable=False, blank=True, null=True)

    uploaded_by = models.TextField(
        editable=False, blank=True, null=True)

    status = models.TextField(
        choices=settings.get_choices(settings.STATUS),
        blank=True, null=True)

    opstatus = models.CharField(
        max_length=255, verbose_name='This update status',
        choices=OPSTATUS,
        blank=True, null=True
    )

    new_id = models.CharField(max_length=255, blank=True, null=True)
    store_filespace = None
    store_doc_catalogue = None

    class Meta:
        ordering = ['site__nzms_sheet', 'site__ordinal', '-ordinal']

    def __unicode__(self):
        if '-' in str(self.site):
            return str(self.site)
        return str(self.site) + '-' + str(self.ordinal)

    def get_absolute_url(self):
        return os.path.join(settings.BASE_URL, str(self))

    url = property(get_absolute_url)

    def display_owner(self):
        if not self.owner:
            return ""
        owner = self.owner
        return owner

    def display_rights(self):
        return markdown(self.rights)

    def display_status(self):
        status = self.status
        if self.opstatus:
            status += '/' + self.opstatus
        return status

    def filespace(self):
        """Return a webnote Directory object for this record.
        """

        if self.store_filespace:
            return self.store_filespace

        path = self.filespace_path()
        docroot = self.url.replace('-', '/')
        baseurl = os.path.join('/static', docroot[1:])

        try:
            d = webnote.Directory(path, docroot, baseurl)
            self.store_filespace = d
        except webnote.Directory.ParseDirNotFound:
            return None

        return self.store_filespace

    def filespace_path(self):
        """Return a string pointing to the object's filespace.

        The filespace for an object is the BASE_FILESPACE setting,
        with the object_id appended. If the object is an update, the
        update identifier is used instead.
        """
        update_id = self.update_id.replace('TMP', '')

        return os.path.join(
            settings.BASE_FILESPACE, self.update_id.replace('-', '/')
        )

    def list_docs(self):
        """Return a list of (link, text tuples) to documents."""
        prefix = os.path.join(
            settings.BASE_URL, self.update_id.replace('-', '/')
        )

        prefix = "/static" + prefix

        if self.filespace:
            return self.filespace().link_docs(prefix)

    def list_figs(self):
        """Return a list of (link, text tuples) to figure files."""
        prefix = os.path.join(
            settings.BASE_URL, self.update_id.replace('-', '/')
        )
        prefix = "/static" + prefix

        if self.filespace:
            return self.filespace().link_figs(prefix)

    def upload_condition(self):

        result = self.condition

        if self.references:
            result += "\n\n### References\n\n"
            result += self.references

        if self.rights:
            result += "\n\n\nRights\n\n"
            result += self.rights

        result = self.replace_temp_ids(result)
        return markdown(result)

    def upload_description(self):

        text = self.finder_aid
        chop = text.split('\r\n\r\n')
        result = ''

        for n in range(0, len(chop)):
            if n == 0:
                pass
            else:
                result += chop[n] + "\n\n"

        result += self.introduction + "\n\n"
        result += self.replace_temp_ids(self.description)

        return markdown(result)

    def update_name(self):
        name = str(self) + ": "
        if self.ordinal == 0:
            return name + "The ArchSite record"

        if self.update_type and self.updated_by:

            name += self.update_type + " by " + self.updated_by

        else:
            name = "Update " + str(self.ordinal)

        return name

    def upload_finder_aid(self):
        text = self.finder_aid

        chop = text.split('\r\n\r\n')
        text = self.replace_temp_ids(chop[0])
        return markdown(text)

    def buttons(self, user):
        """Return a tuple of button commands to be used in the view.

        Buttons on an update record are used to advance or retard it's
        progress through the production process. They are only
        displayed on an update record owned by the user.

        The buttons returned depend on the value in the opstatus field.

            Working        Stage, Stand
            Staging        Complete, Work, Stand
            Completed      Stage
            Standing       Work
        """

        buttons = ()

        if self.owner != user.username:
            return ()

        if self.opstatus == 'Working':
            buttons = ('stage', 'stand', 'hold')

        elif self.opstatus == 'Staging':
            buttons = ('complete', 'work', 'stand', 'hold')

        elif self.opstatus == 'Completed':
            buttons = ('stage', 'hold')

        elif self.opstatus == 'Standing':
            buttons = ('work', 'hold')

        elif self.opstatus == 'Hold':
            buttons = ('work')

        return buttons

    def display_description(self):
        # Reference the text with self, source, baseurl, figures
        result, unref_figs = self.filespace().reference_text(self.description)

        return markdown(result)


class SiteList(models.Model):
    """User-definable lists or groups of sites. """

    URL = 'sitelists'

    sites = models.ManyToManyField(Site, blank=True)

    name = models.CharField(max_length=128)
    long_name = models.CharField(max_length=1024, blank=True, null=True)
    subject = models.TextField(verbose_name='Subject (keywords)')
    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    list_type = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)

#   Record-level authorisation.
    owner = models.CharField(max_length=255, blank=True, null=True)
    edit = models.CharField(max_length=255, blank=True, null=True)
    allow = models.CharField(max_length=255, blank=True, null=True)
    deny = models.CharField(max_length=255, blank=True, null=True)

#   Common metadata fields.
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name='Record created at')

    created_by = models.CharField(
        max_length=255, editable=False, verbose_name='Record created by')

    modified = models.DateTimeField(
        null=True, blank=True, auto_now=True,
        editable=False, verbose_name='Record modified at')

    modified_by = models.CharField(
        max_length=255, null=True, blank=True,
        editable=False, verbose_name='Record modified by')

    notifications = []

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return os.path.join(settings.BASE_URL, self.URL, str(self.id))

    url = property(get_absolute_url)

    def remove_sites(self, ids):
        """Remove a list of sites, check each as valid NZAA id."""

        for item in ids:
            if utils.is_siteid(item):
                self.sites.remove(item)

    def identifiers_str(self):
        """List of nzaa_ids as a string, suitable for injection."""

        ids = list(self.sites.all().values_list('nzaa_id', flat=True))
        identifiers = ""
        for i in ids:
            identifiers += "'" + i + "', "

        # Clip traling comma space.
        return identifiers[:-2]

    def long_fields(self):
        """Return an HTML string representing all the fields.

        """
        result = ''
        if self.description:
            result += '### Description \n\n'
            result += self.description + '\n\n'
        if self.notes:
            result += '### Notes\n\n'
            result += self.notes + '\n\n'

        return markdown(result)

    def sessionlist(self):
        """Return a list of NZAA ids."""

        sessionlist = []
        for site in self.sites.all():
            sessionlist.append(site.nzaa_id)
        return sessionlist


class SiteReview(models.Model):
    """Track review changes to a site record.

    Keep values for changed fields; before and after changes made.

    """

    STATUS = (
        ('live', 'live'),
        ('cancelled', 'cancelled'),
    )

    site = models.ForeignKey(Site, related_name='reviews')
    assessed_by = models.CharField(max_length=255)

    reviewed = models.DateTimeField(
        blank=True, null=True,
        auto_now=True, editable=False,
        verbose_name='Record assessed at'
    )

    log = models.TextField(editable=False)

    status = models.CharField(max_length=255, choices=STATUS)

    note = models.TextField(blank=True, null=True)

    site_name = models.CharField(
        max_length=255, verbose_name='Site name',
        blank=True, null=True)

    site_type = models.CharField(
        blank=True, null=True, max_length=255, choices=Site.SITE_TYPE,
    )

    site_subtype = models.CharField(
        verbose_name='Subtype', choices=Site.SITE_SUBTYPE,
        max_length=255, blank=True, null=True)

    location = models.CharField(max_length=255, blank=True, null=True)

    period = models.CharField(
        max_length=255, choices=Site.PERIOD, blank=True, null=True)

    ethnicity = models.CharField(
        max_length=255, choices=Site.ETHNICITY, blank=True, null=True)

    features = models.CharField(
        max_length=2048, blank=True, null=True,
    )

    radius = models.IntegerField(default=0, blank=True, null=True)

    associated_sites = models.CharField(
        max_length=2048, blank=True, null=True
    )

    recorded = models.DateField(
        verbose_name='Date recorded', blank=True, null=True)

    recorded_by = models.TextField(
        blank=True, null=True, verbose_name='Site recorded by')

    updated = models.DateField(
        blank=True, null=True, verbose_name='Site last updated on')

    updated_by = models.CharField(
        max_length=255,
        blank=True, null=True, verbose_name='Site last updated by')

    visited = models.DateField(
        verbose_name='Visited (date)', blank=True, null=True)

    visited_by = models.CharField(max_length=255, blank=True, null=True)

    record_quality = models.CharField(
        max_length=255, choices=Site.RECORD_QUALITY,
        blank=True, null=True)

#   From fields. Values before this assessment.
    from_site_name = models.CharField(
        max_length=255, verbose_name='Site name',
        blank=True, null=True)

    from_site_type = models.CharField(
        blank=True, null=True, max_length=255, choices=Site.SITE_TYPE,
    )

    from_site_subtype = models.CharField(
        verbose_name='Subtype', choices=Site.SITE_SUBTYPE,
        max_length=255, blank=True, null=True)

    from_location = models.CharField(max_length=255, blank=True, null=True)

    from_period = models.CharField(
        max_length=255, choices=Site.PERIOD, blank=True, null=True)

    from_ethnicity = models.CharField(
        max_length=255, choices=Site.ETHNICITY, blank=True, null=True)

    from_features = models.CharField(
        max_length=2048, blank=True, null=True,
    )

    from_radius = models.IntegerField(default=0, blank=True, null=True)

    from_associated_sites = models.CharField(
        max_length=2048, blank=True, null=True
    )

    from_recorded = models.DateField(blank=True, null=True)
    from_recorded_by = models.TextField(blank=True, null=True)
    from_updated = models.DateField(blank=True, null=True)
    from_updated_by = models.CharField(max_length=255, blank=True, null=True)
    from_visited = models.DateField(blank=True, null=True)
    from_visited_by = models.CharField(max_length=255, blank=True, null=True)
    from_record_quality = models.CharField(
        max_length=255, choices=Site.RECORD_QUALITY,
        blank=True, null=True)

    notifications = []

    def save(self, log=None, *args, **kwargs):

        now = datetime.datetime.now(pytz.utc)
        timestamp = unicode(now.replace(microsecond=0))
        ipno = '127.0.0.1'
        user = 'machine'
        comment = 'Saving from unlogged command.'

        if log:
            ipno = log[0]
            user = log[1]
            comment = log[2]

            line = '\t'.join((timestamp, ipno, user, comment)) + '\n'
            self.log += line

        super(SiteReview, self).save(*args, **kwargs)

    def new_values(self, data):
        """Load new values from something like POST.

        Give it a dictionary containing the field names
        """

        self.location = data.location
        self.recorded_by = data.recorded_by
        self.updated_by = data.updated_by
        self.visited_by = data.visited_by
        self.recorded = data.recorded
        self.visited = data.visited
        self.updated = data.updated
        self.site_type = data.site_type
        self.site_subtype = data.site_subtype
        self.period = data.period
        self.ethnicity = data.ethnicity
        self.record_quality = data.record_quality

        return 0

    def set_new_values(self, site):
        """Change local old location values from a site object."""

        self.location = site.location
        self.recorded_by = site.recorded_by
        self.updated_by = site.updated_by
        self.visited_by = site.visited_by
        self.recorded = site.recorded
        self.visited = site.visited
        self.updated = site.updated
        self.site_type = site.site_type
        self.site_subtype = site.site_subtype
        self.period = site.period
        self.ethnicity = site.ethnicity
        self.record_quality = site.record_quality

        return 0

    def set_old_values_dep(self, site):
        """Change local old location values from a site object."""

        self.from_location = site.location
        self.from_recorded_by = site.recorded_by
        self.from_updated_by = site.updated_by
        self.from_visited_by = site.visited_by
        self.from_recorded = site.recorded
        self.from_visited = site.visited
        self.from_updated = site.updated
        self.from_site_type = site.site_type
        self.from_site_subtype = site.site_subtype
        self.from_period = site.period
        self.from_ethnicity = site.ethnicity
        self.from_record_quality = site.record_quality

        return 0

    def get_new_values(self):
        """Return a dictionary which can be used for updating site record."""

        new_values = {
            'site_type': self.site_type,
            'site_subtype': self.site_subtype,
            'location': self.location,
            'period': self.period,
            'ethnicity': self.ethnicity,
            'recorded': self.recorded,
            'recorded_by': self.recorded_by,
            'updated': self.updated,
            'updated_by': self.updated_by,
            'visited': self.visited,
            'visited_by': self.visited_by,
            'record_quality': self.record_quality,
            'assessment_notes': self.note,
        }

        return new_values

    def get_old_values(self):
        """Return a dictionary which can be used for updating site record."""

        old_values = {
            'site_type': self.from_site_type,
            'site_subtype': self.from_site_subtype,
            'location': self.from_location,
            'period': self.from_period,
            'ethnicity': self.from_ethnicity,
            'recorded': self.from_recorded,
            'recorded_by': self.from_recorded_by,
            'updated': self.from_updated,
            'updated_by': self.from_updated_by,
            'visited': self.from_visited,
            'visited_by': self.from_visited_by,
            'record_quality': self.from_record_quality,
        }

        return old_values
