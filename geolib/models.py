"""Models for the geographic data library.

These models describe index layers and background mapping data. Their
main purpose is to provide indices for the raster data collections
(such as the aerial imagery and lidar tiles), and to provide
searchability on names such as roads, rivers and places.

"""

from __future__ import unicode_literals
from django.contrib.gis.db import models
from django.contrib.gis.geos import MultiPolygon

import datetime
import ephem
import markdown2 as markdown
import math
import os
import subprocess
import urllib2
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import fromstr

import settings
import nzaa.analyse
import nzaa.settings
import nzaa.models 


class Files(models.Model):
    """Abstract class containing URIs for files.

    This can be subclassed to provide a table linking file URIs to
    other library objects, for example, the historic plans, and the
    airphoto indices.

    The filename may have spaces (although I would prefer them not
    to). The URI will be stored with HTML special characters (eg. %20
    representing a space character).

    """
    class Meta:
        abstract = True

    filename = models.CharField(max_length=255)
    uri = models.CharField(max_length=1024)
    file_format = models.CharField(max_length=255)
    received = models.DateField()
    received_fname = models.CharField(max_length=255)
    uploaded = models.DateField(blank=True, null=True)
    uploaded_by = models.CharField(max_length=255, blank=True, null=True)
    provenance = models.TextField()
    notes = models.TextField(blank=True, null=True)


class AerialSurvey(models.Model):
    """Footprint and metadata concerning relevant aerial surveys."""

    URL = '/geolib/airphoto'
    FILESPACE = os.path.join(settings.BASE_FILESPACE, 'airphoto_historic')
    RETROLENS = 'https://files.interpret.co.nz/Retrolens/Imagery/'

    FILM_TYPE = (
        ('B&W', 'B&W',),
        ('colour', 'colour'),
        ('infrared', 'infrared'),
    )

    identifier = models.CharField(max_length=255, primary_key=True)
    ordinal = models.IntegerField(editable=False)
    name = models.CharField(max_length=1024, blank=True, null=True)
    year_first = models.PositiveIntegerField(blank=True, null=True)
    year_last = models.PositiveIntegerField(blank=True, null=True)
    film_type = models.CharField(
        max_length=255, choices=FILM_TYPE, blank=True, null=True)
    rights = models.CharField(max_length=255, blank=True, null=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193, blank=True, null=True)

    class Meta:
        ordering = ('ordinal',)

    def save(self, *args, **kwargs):
        if not os.path.isdir(self.filespace()):
            os.mkdir(self.filespace())

        super(AerialSurvey, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.identifier

    def _url(self):
        return os.path.join(self.URL, self.identifier)

    url = property(_url)

    def filespace(self):
        return os.path.join(self.FILESPACE, self.id)

    def sn(self):
        """Return a string survey number. """

        if self.ordinal:
            return str(self.ordinal)
        if self.id[:2] == 'SN':
            return self.id[2:]

    def frame_count(self):
        frame_count = 0
        for run in self.runs.all():
            frame_count += run.frames.all().count()
        return frame_count

    def georef_frames(self):
        """Return a queryset of georeferenced frames for this survey."""

        s = AerialFrame.objects.filter(run__survey=self)
        return s.filter(status='polynomial')

    def get_next_record(self):
        s = AerialSurvey.objects.all()
        index = None

    def compute_footprint(self, commit=False):
        """Return a multipolygon geometry of all the runs in this survey.

        If the attribute 'commit' is True, the geometries in the
        records will be changed with a save() command. This propigates
        to the run records also.

        """

        footprint = None
        runs = self.runs.all()

        if not runs:
            return None

        footprint = runs[0].compute_footprint(commit=commit)

        for run in runs[1:]:
            runprint = run.compute_footprint(commit=commit)
            if runprint:
                if not footprint:
                    footprint = runprint
                else:
                    footprint = footprint.union(runprint)

        if commit:
            try:
                self.geom = MultiPolygon(footprint)
            except TypeError:
                self.geom = footprint
            self.save()

        return footprint


# Legacy code, not checked.
class AerialRun(models.Model):
    """Footprint and metadata for survey runs.

    The identifier is a string, and the ordinal is an integer derived
    from that string.

    """

    survey = models.ForeignKey(AerialSurvey, related_name='runs')
    identifier = models.CharField(max_length=16)
    ordinal = models.IntegerField(blank=True, null=True)
    direction = models.CharField(max_length=255, blank=True, null=True)
    rights = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193, blank=True, null=True)

    class Meta:
        ordering = ('survey', 'ordinal')

    def save(self, *args, **kwargs):
        if not os.path.isdir(self.filespace()):
            os.mkdir(self.filespace())

        self.ordinal = self.find_ordinal()

        super(AerialRun, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.identifier

    name = property(__unicode__)

    def _url(self):
        return os.path.join(self.survey.url, self.rn())

    url = property(_url)

    def filespace(self):
        return os.path.join(self.survey.FILESPACE, self.identifier)

    def rn(self):
        """Return a string run number."""

        parts = self.identifier.split('/')
        return parts[1]

    def compute_footprint(self, commit=False):
        """Return a multipolygon geometry of all the frames in this run.
        """

        footprint = None
        frames = self.frames.exclude(geom=None)
        if frames:
            footprint = MultiPolygon(frames[0].geom)

            for frame in frames[1:]:
                footprint = frame.geom.union(footprint)

        if commit:
            try:
                self.geom = footprint
            except:
                self.geom = MultiPolygon(footprint)

            self.save()

        return footprint

    def find_ordinal(self):
        """Return an integer ordinal."""

        survey, run = self.identifier.split('/')

        try:
            ordinal = int(run)
        except ValueError:
            ordinal = None

        return ordinal

    def georef_frames(self):
        """Return a queryset of georeferenced frames for this survey."""

        s = AerialFrame.objects.filter(run=self).order_by('identifier')
        return s.filter(status='polynomial')


class AerialFrame(models.Model):
    """Aerial photo frames. Not aerial imagery.

    Metadata pertaining to the aerial photography collection.

    These images are sourced from http://retrolens.nz, and are in
    various stages of georeference.

    The name field is provided as an alternative identifier to the
    survey/run/frame identifiers. The description text field is
    intended to hold georeferencing notes.

    """

    STATUS = (
        (None, '-'),
        ('for reference', 'for reference'),
        ('polynomial', 'polynomial'),
        ('thin plate spline', 'thin plate  spline'),
    )
    FILESPACE = os.path.join(settings.BASE_FILESPACE, 'airphoto_historic')
    STATIC_URL = os.path.join(settings.STATIC_URL, 'geolib/airphoto_historic')

    latitude = None
    longitude = None
    azimuth = None
    altitude = None

    run = models.ForeignKey(AerialRun, related_name='frames')
    identifier = models.CharField(max_length=16)
    ordinal = models.IntegerField(blank=True, null=True)
    date_flown = models.DateField(blank=True, null=True)
    time_flown = models.TimeField(blank=True, null=True)
    alt_ft = models.PositiveIntegerField(blank=True, null=True)
    alt_m = models.PositiveIntegerField(blank=True, null=True)
    focal_length = models.CharField(max_length=16, blank=True, null=True)
    aperture = models.CharField(max_length=32, blank=True, null=True)

    status = models.CharField(
        max_length=255, choices=STATUS, default=None, blank=True, null=True)

    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    georef_notes = models.TextField(blank=True, null=True)

    source_url = models.CharField(max_length=2014, blank=True, null=True)
    coverage = models.CharField(max_length=255, blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    rights = models.CharField(max_length=255, blank=True, null=True)

    geom = models.PolygonField(srid=2193, blank=True, null=True)

    class Meta:
        ordering = ('run', 'ordinal')

    def save(self, *args, **kwargs):
        if not os.path.isdir(self.filespace()):
            os.mkdir(self.filespace())

        self.ordinal = self.find_ordinal()

        super(AerialFrame, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.identifier

    def get_absolute_url(self):
        return os.path.join(self.run.url, self.fn())

    url = property(get_absolute_url)

    def _get_identifier(self):
        """Return a string identifier.
        """

        identifier = 'unknown'

        if self.survey and self.run and self.frame:
            identifier = (
                str(self.survey) + '/' +
                str(self.run) + '/' +
                str(self.frame)
            )

        return identifier

    def filespace(self):
        return os.path.join(self.run.survey.FILESPACE, self.identifier)

    def find_ordinal(self):
        """Return an integer ordinal."""

        survey, run, frame = self.identifier.split('/')

        try:
            ordinal = int(frame)
        except ValueError:
            ordinal = None

        return ordinal

    def fn(self):
        parts = self.identifier.split('/')
        return parts[-1]

    def lidar_set(self):
        if not self.geom:
            return None
        if self.lidar_tiles().count():
            return self.lidar_tiles()[0].series
        return None

    def lidar_tiles(self):
        """Lidar tiles intersecting with this photo."""
        if not self.geom:
            return None
        return LidarTile.objects.filter(
            geom__intersects=self.geom)

    def ortho(self):
        """Orthophoto tiles intersecting with this tile."""
        if not self.geom:
            return None
        return OrthoTile.objects.filter(
            geom__intersects=self.geom)

    def sites(self):
        """NZAA sites within the footprint of this frame."""
        if not self.geom:
            return None
        return nzaa.models.Site.objects.filter(geom__intersects=self.geom)

    def ephemera(self):
        """Return solar azimuth and altitude.

        These values are computed on the day and time the frame was
        taken. They can be used to generate hillshade images with the
        same lighting values as the photograph, to aid in
        georeferencing.

        """

        if not self.geom:
            return None

        p = self.geom.centroid
        p.transform(4326)
        self.latitude = p.y
        self.longitude = p.x

        if not self.date_flown:
            return None
        if not self.time_flown:
            return None

        O = ephem.Observer()
        O.lon, O.lat = str(p.x), str(p.y)

        date = datetime.datetime(
            self.date_flown.year,
            self.date_flown.month,
            self.date_flown.day,
            self.time_flown.hour,
            self.time_flown.minute,
            self.time_flown.second,
        )
        shift = datetime.timedelta(0, 0, 0, 0, 0, 12)
        date = date - shift
        O.date = date
        S = ephem.Sun()
        S.compute(O)

        self.azimuth = S.az
        self.altitude = ephem.degrees(S.alt)

        return None

    def lat(self):
        if self.latitude:
            return self.latitude
        self.ephemera()
        return self.latitude

    def lon(self):
        if self.longitude:
            return self.longitude
        self.ephemera()
        return self.longitude

    def az(self):
        if self.azimuth:
            return self.azimuth
        self.ephemera()
        return self.azimuth

    def alt(self):
        if self.altitude:
            return self.altitude
        self.ephemera()
        return self.altitude

    def dms2dd(self, dms):
        """Degrees, minutes, seconds to digital degrees.

        Accepts an Angle object from the ephem package. This is
        encoded as a float containing an angle in radians. The
        conversion is done using the standard formula for converting
        radians into degrees.

        """
        if dms:
            return dms * (180 / math.pi)

        return None

    def alt_dd(self):
        """Altitude as digital degrees (float)."""
        return self.dms2dd(self.alt())

    def az_dd(self):
        """Azimuth as digital degrees (float)."""
        return self.dms2dd(self.az())

    def thumbnail(self):
        """Return an image link tuple to the thumbnail image."""

        fname = self.run.survey.sn() + '_' + self.run.rn()
        fname += '-' + self.fn() + '_512.jpg'
        src = os.path.join(
            self.STATIC_URL, self.identifier, fname
        )
        alt = self.identifier

        return (src, alt)

    def retrolens(self):
        """Return a list of link tuples to original files. """

        url = self.get_retrolens_url()
        links = [
            (os.path.join(url, 'High.jpg'), "High resolution"),
            (os.path.join(url, 'Med.jpg'), "Medium resolution"),
        ]

        return links

    def get_retrolens_url(self):
        """Return string being the address of the original image file."""

        url = self.run.survey.RETROLENS + 'SN' + self.run.survey.sn()
        url += '/Crown_' + self.run.survey.sn() + '_'
        url += self.run.rn() + '_' + self.fn() + '/'
        return url

    def files_available(self):
        """True if retrolens has files available."""

        base_url = self.get_retrolens_url()
        high = os.path.join(base_url, 'High.jpg')
        med = os.path.join(base_url, 'Med.jpg')

        try:
            response = urllib2.urlopen(med)
        except urllib2.HTTPError:
            return False

        return True

    def download_source_files(self):
        """Go get copies of the photo from from Retrolensnz."""

        base_url = self.get_retrolens_url()
        high = os.path.join(base_url, 'High.jpg')
        med = os.path.join(base_url, 'Med.jpg')

        fname = self.run.survey.id.replace('SN', '')
        fname += '_' + self.run.rn() + '-'
        fname += self.fn()

        fname_med = fname + '_med.jpg'
        dest_med = os.path.join(self.filespace(), fname_med)

        try:
            response = urllib2.urlopen(med)
        except urllib2.HTTPError:
            pass

        f_med = open(dest_med, 'w')
        f_med.write(response.read())
        f_med.close()
        response.close()

        fname_high = fname + '.jpg'
        dest_high = os.path.join(self.filespace(), fname_high)

        try:
            response = urllib2.urlopen(high)
        except urllib2.HTTPError:
            pass

        f_high = open(dest_high, 'w')
        f_high.write(response.read())
        f_high.close()
        response.close()

    def write_exif(self):
        """Produce an exif compatable structure to write into a file.
        """
        return None

    def thumbnails(self):
        """List of links to the 512px thumbnails held in filespace."""

        thumbs = []

        for f in sorted(os.listdir(self.filespace())):
            if "_512" in f:
                alt = f
                src = os.path.join(
                    settings.STATIC_URL, self.STATIC_URL,
                    self.identifier, f,
                    )
                thumbs.append((src, alt))

        return thumbs


class AerialFile(Files):
    """All files associated with an aerial photo frame.

    """

    FILETYPE = (
        ('crop', 'crop'),
        ('points', 'points'),
        ('ref_high', 'ref_high'),
        ('ref_low', 'ref_low'),
        ('source_high', 'source_high'),
        ('source_low', 'source_low'),
    )
    filetype = models.CharField(max_length=255, choices=FILETYPE)
    geom = models.PolygonField(srid=2193, blank=True, null=True)


class Cadastre(models.Model):
    """NZ mainland property parcels, sourced from LINZ.

    """

    URL = os.path.join(settings.BASE_URL, 'cadastre')

    appellation = models.TextField(blank=True, null=True)
    affected_surveys = models.TextField(blank=True, null=True)
    parcel_intent = models.TextField(blank=True, null=True)
    topology_type = models.TextField(blank=True, null=True)
    statutory_actions = models.TextField(blank=True, null=True)
    land_district = models.TextField(blank=True, null=True)
    titles = models.TextField(blank=True, null=True)
    survey_area = models.FloatField(blank=True, null=True)
    calc_area = models.FloatField(blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193)

    def closest_placenames(self):
        """Return a list (placename, distance(m)) tuples of the closest places.

        Return the three closest named places to this site.

        """

        i1 = PlaceName.objects.filter(
            geom__distance_lte=(self.geom, D(m=10000)))
        i2 = i1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

        places = []

        for i in range(0, 3):
            place = i2[i]
            place.distance = self.geom.distance(i2[i].geom)
            places.append(place)

        return places

    def closest_road(self):
        """Return a (name, distance) tuple for the road line closest.

        """

        i1 = Topo50_Road.objects.filter(
            geom__distance_lte=(self.geom, D(m=10000)))
        i2 = i1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

        if len(i2) > 0:
            road = i2[0]
            road.distance = self.geom.distance(i2[0].geom)

            return road

        return None

    def closest_sites(self, count=5):
        """Return the site record closest to this parcel."""

        i1 = nzaa.models.Site.objects.filter(
            geom__distance_lte=(self.geom, D(m=10000)))
        i2 = i1.annotate(
            distance=Distance('geom', self.geom)).order_by('distance')

        if len(i2) > 0:
            if len(i2) < count:
                count = len(i2)

            sites = []
            for n in range(count):
                site = i2[n]
                site.distance = self.geom.distance(i2[n].geom)
                sites.append(site)
            return sites

        return None

    def handle(self):
        if self.appellation:
            return self.appellation
        return self.parcel_intent

    def parcels_intersecting(self):
        """Return a list of parcels touching this one."""
        return Cadastre.objects.filter(geom__touches=self.geom)

    def region(self):
        """Return the district this cadastral parcel is in."""

        return Region.objects.filter(geom__intersects=self.geom)

    def sites_adjacent(self):
        """Archaeological sites within parcels adjacent to this one."""

        parcels = self.parcels_intersecting()
        study_area = parcels[0].geom
        for parcel in parcels:
            if parcel.id == self.id:
                pass
            else:
                study_area = study_area.union(parcel.geom)

        sites = nzaa.models.Site.objects.filter(geom__intersects=study_area)
        for site in sites:
            site.distance = self.geom.distance(site.geom)

        return sites

    def sites_intersecting(self):
        """Archaeological sites whose footprint intersects this parcel.
        """

        return nzaa.models.Site.objects.filter(
            geom__intersects=self.geom)

    def sites_buffer(self, dist=500):
        """Sites within 500m (default) of this parcel.
        """

        study_area = self.geom.buffer(width=dist)
        sites = nzaa.models.Site.objects.filter(
            geom__intersects=study_area)
        sites = sites.exclude(geom__intersects=self.geom)
        site_ids = []
        for site in sites:
            site.distance = self.geom.distance(site.geom)

        return sites

    def sites_within(self):
        """Archaeological sites with point location within this parcel.
        """

        return nzaa.models.Site.objects.filter(geom__intersects=self.geom)

    def ta(self):
        """Return the district this cadastral parcel is in."""

        return TerritorialAuthority.objects.filter(geom__intersects=self.geom)

    def get_absolute_url(self):
        return os.path.join(self.URL, str(self.id))

    url = property(get_absolute_url)


class LidarSet(models.Model):
    """Source of the airimage tiles.

    This is usually an LINZ airimage layer. This layer is an index, so
    we can see quickly if a site lies within a known aerial image set.

    """

    URL = os.path.join(settings.BASE_URL, 'lidar')

    identifier = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=1024, blank=True, null=True)
    year_captured = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    imagelayer_uri = models.CharField(max_length=1024, blank=True, null=True)

    geom = models.MultiPolygonField(srid=2193, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return os.path.join(self.URL, self.identifier)

    url = property(get_absolute_url)


class LidarTile(models.Model):
    """Index to lidar tiles.

    Each tile can have several files associated with it: The DEM (in
    ASCII and/or TIFF), zero or many hillshade images, an intensity
    image. Objects in this class will be aware of all these files.

    """

    DIRECTORY = os.path.join(settings.STATICFILES_DIRS[0], 'geolib')
    FILESPACE = os.path.join('/srv/geolib/', 'lidar')
    STATIC_URL = os.path.join(settings.STATIC_URL, 'geolib/lidar')

    series = models.ForeignKey(LidarSet, related_name='tiles')
    identifier = models.CharField(max_length=255)
    provenance = models.TextField(blank=True, null=True)
    local_fname = models.CharField(max_length=255, blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193)

    class Meta:
        ordering = ('identifier',)

    def __unicode__(self):
        return self.identifier

    def get_absolute_url(self):
        return os.path.join(self.series.url, self.identifier)

    url = property(get_absolute_url)

    def path_dem(self):
        """Return the full path to the DEM file."""

        series = {
            'wrls2008': 'lidar_wrc2008',
            'wrls2011': 'lidar_wrc2010',
            'AUK2015': 'lidar_AUK2015',
            'BOP2015': 'lidar_BOP2015',
            'CANT2015': 'lidar_CANT2015',
            'WAICOAST2015': 'lidar_WAICOAST2015',
            'WELL2013': 'lidar_WELL2013',
        }

        (sheet, ordinal) = self.tile_id.split('_')

        directory = '/srv/geolib/' + series[self.series_id]
        filename = self.tile_id.lower() + '_dem-1m.tif'

        fullpath = os.path.join(
            directory,
            sheet.lower(),
            filename
        )

        if os.path.isfile(fullpath):
            return fullpath

        return "### DEM file not found ###\n" + fullpath

    def airphoto(self):
        """Historic aerial photos intersecting with this tile.."""
        if not self.geom:
            return None
        return AerialFrame.objects.filter(
            geom__intersects=self.geom)

    def ortho(self):
        """Orthophoto tiles intersecting with this tile."""
        if not self.geom:
            return None
        return OrthoTile.objects.filter(
            geom__intersects=self.geom)

    def sites(self):
        """NZAA sites which may be visible on this tile."""
        if not self.geom:
            return None
        return nzaa.models.Site.objects.filter(
            geom__intersects=self.geom)

    def staticpath(self):
        (sheet, ordinal) = self.tile_id.split('_')
        path = os.path.join(
            self.STATIC_URL + '_' + str(self.series),
            sheet.lower()
        )
        return path

    def filespace(self):
        return self.FILESPACE + "_" + str(self.series)


class OrthoSet(models.Model):
    """Source of the airimage tiles.

    This is usually a LINZ orthophoto layer. This layer is an index, so
    we can see quickly if a site lies within a known aerial image
    set. The geometry of objects in this table will be computed as the
    union of all geometries of the tiles belonging to this set.

    """

    URL = os.path.join(settings.BASE_URL, 'ortho')
    identifier = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=1024, blank=True, null=True)
    year_captured = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    imagelayer_uri = models.CharField(max_length=1024, blank=True, null=True)

    geom = models.MultiPolygonField(srid=2193, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return os.path.join(self.URL, self.identifier)

    url = property(get_absolute_url)

    def compute_footprint(self, commit=False):
        """Return the union of geometries for all tiles belonging to this set.
        """

        footprint = self.tiles.all()[0].geom
        for tile in self.tiles.all():
            footprint = footprint.union(tile.geom)

        footprint = MultiPolygon(fromstr(footprint))
        if commit:
            print "Saving footprint", self.name
            self.geom = footprint
            self.save()

        return footprint


class OrthoTile(models.Model):
    """Orthorectified aerial imagery, usually orthorectified tiles.

    These are not aerial photographs, which are indexed in the
    Airphoto table.

    """

    URL = os.path.join(settings.BASE_URL, 'ortho')
    FILESPACE = os.path.join('/srv/geolib/', 'ortho')
    STATIC_URL = os.path.join(settings.STATIC_URL, 'geolib/ortho')

    series = models.ForeignKey(OrthoSet, related_name='tiles')
    identifier = models.TextField(verbose_name="Tile id")
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193, blank=True, null=True)
    local_fname = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.series.identifier + " " + self.identifier

    def get_absolute_url(self):
        return os.path.join(self.URL, self.series.identifier, self.identifier)

    url = property(get_absolute_url)

    def staticpath(self):
        (sheet, ordinal) = self.tile.split('_')
        path = os.path.join(
            self.STATIC_URL + '_' + self.series.identifier,
            sheet.lower()
        )
        return path

    def airphoto(self):
        """Historic aerial photos intersecting with this tile.."""
        if not self.geom:
            return None
        return AerialFrame.objects.filter(
            geom__intersects=self.geom)

    def lidar(self):
        """Lidar tiles intersecting with this tile."""
        if not self.geom:
            return None
        return LidarTile.objects.filter(
            geom__intersects=self.geom)

    def sites(self):
        """NZAA sites which may be visible on this frame."""
        if not self.geom:
            return None
        return nzaa.models.Site.objects.filter(
            geom__intersects=self.geom)

    def geoimage(self):

        (sheet, ordinal) = self.identifier.split('_')
        filename = "RGB_" + self.identifier + '.tif'
        fullpath = os.path.join(self.filespace(), sheet.lower(), filename)

        return fullpath

    def _extents(self):

        for pair in self.geom.coords:
            print "geolib.models HERE", pair

        return str(self.geom.coords)

    extents = property(_extents)

    def topo50_sheet(self):
        """Return the name of the Topo50 sheet this tile sits on.

        Make a geographic computation.

        """

        sheet, ordinal = self.tile.split('_')

    # Legacy code. Will need reworking
    def display1024(self):
        """Return an image (src, alt) tuple for the 1024px display copy.

        If there isn't one there, create it.
        """

        (sheet, ordinal) = self.identifier.split('_')
        fname = self.identifier.upper() + '_1024.jpg'
        src = os.path.join(self.staticpath(), 'display', fname)
        alt = str(self)

        displayspace = os.path.join(
            self.filespace(), sheet.lower(), "display"
        )

        path = os.path.join(displayspace, fname)

        if not os.path.isfile(path):
            self.create_display_copy(1024)

        return (src, alt)

    def filespace(self):
        return self.FILESPACE + "_" + str(self.series.identifier)


class TopoMapSeries(models.Model):
    """Series of topographic maps.


    The spatial index for NZMS260 and Topo50 are available from LINZ:

        NZMS260 series
        https://data.linz.govt.nz/layer/51579-nzms-260-map-sheets/

        Topo50 series
        https://data.linz.govt.nz/layer/50295-nz-topo-50-map-sheets/

    The georeferenced map sheets themselves are available from the
    Auckland University:

        NZMS1 series
        https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_001/geotif/


        NZMS260 series
        https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_260/geotif/

    And LINZ

        TOPO50 series
        http://topo.linz.govt.nz/Topo50_raster_images/GeoTIFFTopo50/

    """

    URL = '/geolib/topo/'

    series = models.CharField(max_length=255, primary_key=True)
    letter = models.CharField(max_length=8, blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    source_instution = models.CharField(max_length=255)
    uri = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('series',)

    def __unicode__(self):
        return self.series

    def get_absolute_url(self):
        return os.path.join(self.URL, self.series)

    url = property(get_absolute_url)

    def set_letter_ordinal(self):
        """Set the internal values for letter and ordinal from sheet_id.

        This is annoying, but it makes it possible for sheets to sort
        in the correct order.

        DOES NOT save the record. You have to do that yourself.

        """
        letter = ''
        ordinal = 0

        if self.series == 'NZMS1':
            letter = ''
            ordinal = 0

        if self.series == 'NZMS260':
            letter = ''
            ordinal = 0

        if self.series == 'TOPO50':
            letter = ''
            ordinal = 0

        self.letter = letter
        self.ordinal = ordinal


class TopoMap(models.Model):
    """Index to the maps collection.

    This table indexes map sheets for which images are held. These
    images are raster files which can be displayed in a GIS.

    The index files indicate coverage of named sheets. Some of these
    have inclusions from adjacent sheets. This table records the named
    sheet footprints, and so differs from the series grids (NZMSgrid
    and Topo50grid).
    """

    LIBRARY = os.path.join(settings.STATICFILES_DIRS[0], 'geolib',)
    SERIES = (
        ('NZMS1', 'NZMS1'),
        ('NZMS260', 'NZMS260'),
        ('TOPO50', 'TOPP50'),
        ('TOPO250', 'TOPO250'),
    )
    SOURCES = {
        'NZMS1': 'https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_001/geotif/',
        'NZMS260':
            'https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_260/geotif/',
        'TOPO50':
            'http://topo.linz.govt.nz/Topo50_raster_images/GeoTIFFTopo50/',
    }
    URL = '/geolib/topo/'

    name = models.CharField(max_length=255, blank=True, null=True)
    sheet_id = models.CharField(max_length=255, blank=True, null=True)

    series = models.ForeignKey(TopoMapSeries, related_name='sheets')

    projection = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    local_fname = models.CharField(max_length=255, blank=True, null=True)

    # Geom is a multipolygon, to aid with importing from shapefiles.
    geom = models.MultiPolygonField(srid=2193)

    class Meta:
        ordering = ('series', 'sheet_id')

    def __unicode__(self):
        if self.name:
            return self.sheet_id + ' ' + self.name
        return self.sheet_id

    def get_absolute_url(self):
        return os.path.join(self.series.url, str(self.id))

    url = property(get_absolute_url)

    def banner(self):
        """Tuple (src, alt) for the display image for this sheet,.

        This is taken as the first file in the list of associated files.
        """

        if self.files.all().count() > 1:
            f = self.files.all()[0]
            (basename, ext) = os.path.splitext(f.filename)

            src = os.path.join(
                '/static/geolib/map_' + self.series.series.lower(),
                'view', basename + '.png'
            )
            alt = f.filename

            return (src, alt)
        return None

    def display_name(self):
        """Return a string identifying the sheet, for simple display."""

        name = str(self.series) + " " + self.sheet_id + " "
        name += self.name

        return name

    def source_url(self):
        """Points to the part of of the internet where you can get the geotiff.
        """

        return os.path.join(self.SOURCES[self.series], self.local_fname)

    def sites(self):
        """A queryset of all nzaa.Site objects intersecting this."""
        return nzaa.models.Site.objects.filter(geom__intersects=self.geom)

    def sites_by_lgcy_type(self):
        analysis = nzaa.analyse.nzaa.models.Site(self.sites())
        return analysis.count_by_lgcy_type()

    def xmin(self):
        return int(self.geom.extent[0])

    def ymin(self):
        return int(self.geom.extent[1])

    def xmax(self):
        return int(self.geom.extent[2])

    def ymax(self):
        return int(self.geom.extent[3])


class TopoMapFile(Files):
    """Catalogue of GeoTiff files for topographic maps.

    The contents of this table will be built once, then remain mostly
    unchanging, except for the occasional possible edition updates in
    Topo50 series.

    """

    URL = '/geolib/topo/geotif/'

    sheet = models.ForeignKey(TopoMap, related_name='files')

    def __unicode__(self):
        return self.filename

    def get_absolute_url(self):
        return os.path.join(self.URL, self.filename)

    url = property(get_absolute_url)

    def banner(self):
        basename, ext = os.path.splitext(self.filename)
        src = os.path.join(
            '/static/geolib/map_' + self.sheet.series.series.lower(),
            'view', basename + '.png'
        )
        alt = self.filename

        return (src, alt)


class NZMSgrid(models.Model):
    """Contains the NZMS260 mapping grid without map sheet overlays.

    Used in the NZAA application for predicting the site identifier.
    """

    identifier = models.CharField(max_length=4, primary_key=True)
    sheet_name = models.TextField(blank=True, null=True)
    geom = models.PolygonField(srid=2193)

    record_region = models.CharField(max_length=255, blank=True, null=True)

    nzms_xmax = models.IntegerField()
    nzms_xmin = models.IntegerField()
    nzms_ymax = models.IntegerField()
    nzms_ymin = models.IntegerField()

    nztm_xmax = models.FloatField()
    nztm_xmin = models.FloatField()
    nztm_ymax = models.FloatField()
    nztm_ymin = models.FloatField()

    def __unicode__(self):
        return self.identifier


class PlaceName(models.Model):
    """From the NZ Place names Gazetteer.

    Available from LINZ at
    https://data.linz.govt.nz/layer/51681-nz-place-names-nzgb/
    """

    name = models.TextField()
    status = models.TextField(blank=True, null=True)
    feat_type = models.TextField(blank=True, null=True)
    nzgb_ref = models.CharField(max_length=255, blank=True, null=True)
    land_district = models.TextField(blank=True, null=True)
    info_ref = models.TextField(blank=True, null=True)
    info_origin = models.TextField(blank=True, null=True)
    info_description = models.TextField(blank=True, null=True)
    desc_code = models.TextField(blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    geom = models.PointField(srid=2193)

    def __unicode__(self):
        return self.name


class Region(models.Model):
    """The Region layer from Statistics NZ.

    https://datafinder.stats.govt.nz/layer/25738-regional-council-2013/
    """

    identifier = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return os.path.join('/nzaa', self.identifier)

    url = property(get_absolute_url)

    def sites_count(self):
        return nzaa.models.Site.objects.filter(region=self.name).count()


class TerritorialAuthority(models.Model):
    """The TA layer from Statistics NZ.

    We require clipped TA boundaries, These are available to download
    along with a huge package, from Stats NZ

        http://archive.stats.govt.nz/browse_for_stats/Maps_and_geography/
        Geographic-areas/digital-boundary-files.aspx

    The version I've selected is the top of the list of ESRI
    shapefiles, New Zealand 2017 clipped high def (NZTM) (616MB)

    The URL is too horrid to show.

    """

    identifier = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193)


class Topo50grid(models.Model):
    """Contains the Topo50 mapping grid without map sheet overlays.

    Used in the NZAA application for predicting the site identifier.

    This grid can be generated using code in the nzaa.utils module. It
    depends on having the Topo50_islands table populated before
    running the code.

    """

    identifier = models.CharField(max_length=4, primary_key=True)
    sheet_name = models.TextField(blank=True, null=True)
    geom = models.PolygonField(srid=2193)

    nzms_xmax = models.IntegerField()
    nzms_xmin = models.IntegerField()
    nzms_ymax = models.IntegerField()
    nzms_ymin = models.IntegerField()


class TopoContour20Metre(models.Model):
    """Contours from the Topo50 dataset.

    Available from LINZ at

        https://data.linz.govt.nz/layer/50768-nz-contours-topo-150k/

    """

    elevation = models.IntegerField()
    provenance = models.TextField(blank=True, null=True)
    topo50 = models.TextField(blank=True, null=True)
    geom = models.MultiLineStringField(srid=2193)


class Topo50_Island(models.Model):
    """Topo50 Coastlands and Islands polygons.

    Available from LINZ at

        https://data.linz.govt.nz/layer/\
        51153-nz-coastlines-and-islands-polygons-topo-150k/
    """

    identifier = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    group = models.CharField(max_length=255, blank=True, null=True)
    provenance = models.TextField()
    geom = models.MultiPolygonField(srid=2193)


class Topo50_Lake(models.Model):
    """Topo50 Lakes polygons.

    Available from LINZ at

        https://data.linz.govt.nz/layer/50293-nz-lake-polygons-topo-150k/

    """

    name = models.CharField(max_length=255, blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193)

    def __unicode__(self):
        return self.name


class Topo50_Rail(models.Model):
    """Topo50 railway centrelines.

    Available from LINZ at
    https://data.linz.govt.nz/layer/50319-nz-railway-centrelines-topo-150k/
    """

    name = models.CharField(max_length=255, blank=True, null=True)
    track_type = models.CharField(max_length=255, blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiLineStringField(srid=2193)


class Topo50_RiverLine(models.Model):
    """Topo50 river centrelines.

    Available from LINZ at

        https://data.linz.govt.nz/layer/50327-nz-river-centrelines-topo-150k/
    """

    name = models.CharField(max_length=255, blank=True, null=True)
    stream_order = models.PositiveIntegerField(blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiLineStringField(srid=2193)


class Topo50_RiverPoly(models.Model):
    """Topo50 river polygons.

    Available from LINZ at

        https://data.linz.govt.nz/layer/50328-nz-river-polygons-topo-150k/

    """

    name = models.CharField(max_length=255, blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiPolygonField(srid=2193)


class Topo50_Road(models.Model):
    """Topo50 road centrelines.

    Available from LINZ at

    https://data.linz.govt.nz/layer/50329-nz-road-centrelines-topo-150k/data/

    """

    name = models.TextField(blank=True, null=True)
    hway_num = models.CharField(max_length=255, blank=True, null=True)
    lane_count = models.IntegerField(blank=True, null=True)
    way_count = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    surface = models.CharField(max_length=255, blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    geom = models.MultiLineStringField(srid=2193)

    def __uniclde__(self):
        return str(self.id) + " " + self.name


class Waterways(models.Model):
    """Provide a reference layer of waterway centrelines.

    Include selected named and unnamed rivers and creeks, and named
    coastlines.

    These are traced indivdually from Topo50 map images, with
    coastlines compiled from LINZ Topo50 data.

    """

    base_name = models.CharField(max_length=255, blank=True, null=True)
    type_name = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    provenance = models.TextField(blank=True, null=True)
    geom = models.LineStringField(srid=2193, blank=True, null=True)
