"""Utilities. Useful little routines.

"""

import datetime
import os
import pytz

from django.contrib.gis.geos import Polygon


from bs4 import BeautifulSoup
import requests

import models
import settings


class CreateAirphotoRecords():
    """Given a string identifier, do all necessaries to create survey, run
    and frame records.

    """

    identifier = None
    survey = None
    run = None
    frame = None
    survey_id = None
    rn = None
    fn = None
    notifications = []

    def __init__(self, identifier=None):
        s = False
        if identifier:
            try:
                s = self.validate_identifier(identifier)
            except self.InvalidRunNumber:
                self.rn = 'invalid'
            except self.InvalidFrameNumber:
                self.fn = 'invalid'

        if s:
            self.survey, self.run, self.frame = self.survey_run_frame(
                identifier)

    def create_records(self, data, identifier=None):
        """Sequencer. Create and return survey, run and frame records.

        Depends on
        """

        if identifier:
            try:
                s = self.validate_identifier(identifier)
            except self.InvalidRunNumber:
                self.rn = 'invalid'
            except self.InvalidFrameNumber:
                self.fn = 'invalid'

            if s:
                self.survey, self.run, self.frame = self.survey_run_frame(
                    identifier)

        identifier = self.identifier

        if not identifier:
            raise self.NoIdentifierSupplied()

        if not self.survey:
            self.survey = self.create_survey(data)

        data['survey'] = self.survey

        if not self.run:
            self.run = self.create_run(data)

        data['run'] = self.run

        self.frame = self.create_frame(data)

        if self.frame.files_available():
            self.notifications.append(
                'Creating AerialFrame record ' + self.frame.identifier)
            self.survey.save()
            self.run.save()
            self.frame.save()
            self.frame.download_source_files()
        else:
            self.notifications.append(
                'Source files not available' + self.frame.identifier)

    def create_survey(self, data):
        survey = models.AerialSurvey()
        survey.id = data['id']
        survey.name = data['name']
        survey.ordinal = int(data['id'].replace('SN', ''))
        survey.year_first = data['year_first']
        survey.year_last = data['year_last']
        survey.film_type = data['film_type']
        survey.rights = data['rights']
        survey.comments = data['comments']

        return survey

    def create_run(self, data):
        run = models.AerialRun()
        run.survey = data['survey']
        run.identifier = self.survey.id + '/' + self.rn

        return run

    def create_frame(self, data):
        frame = models.AerialFrame()
        frame.run = self.run
        frame.identifier = self.identifier
        frame.coverage = data['coverage']
        frame.date_flown = data['date_flown']
        frame.status = data['status']

        return frame

    def validate_identifier(self, identifier):
        """Return True if string a valid identifier.

        To be a valid identifier the string must pass these tests:

        -   split into 3 elements by '/' character.
        -   last of 3 elements to be an integer.
        -   middle of three elements to be an integer or a member
            of the list of valid run values.

        If valid, will set global values and return True.

        """

        ids = identifier.split('/')
        if len(ids) != 3:
            raise self.InvalidIdentifier(identifier)

        try:
            rn = int(ids[1])
            rn = ids[1]
        except ValueError:
            if ids[1] in settings.VALID_RUN_IDS:
                rn = ids[1]
            else:
                raise self.InvalidRunNumber(identifier)
        try:
            fn = int(ids[2])
            fn = ids[2]
        except ValueError:
            raise self.InvalidFrameNumber(identifier)

        self.identifier = identifier
        self.survey_id = ids[0]
        self.rn = rn
        self.fn = fn

        return True

    def survey_run_frame(self, identifier):
        """Given a string identifier, return a tuple of records."""
        survey = None
        run = None
        frame = None

        ids = identifier.split('/')
        if len(ids) == 3:
            s = ids[0]
            r = ids[1]
            f = ids[2]
            run_id = s + '/' + r
        else:
            return (None, None, None)

        try:
            survey = models.AerialSurvey.objects.get(id=s)
        except models.AerialSurvey.DoesNotExist:
            return (None, None, None)

        try:
            run = models.AerialRun.objects.get(identifier=run_id)
        except models.AerialRun.DoesNotExist:
            return (survey, None, None)

        try:
            frame = models.AerialFrame.objects.get(
                run__survey=survey, run=run, ordinal=int(f))
        except models.AerialFrame.DoesNotExist:
            frame = None

        return (survey, run, frame)

    class InvalidFrameNumber(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    class InvalidIdentifier(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    class InvalidRunNumber(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    class NoIdentifierSupplied(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)


def rotate_run(run, direction):
    """"Produce a set of shell commands to rotate the images in a run.

    There are two files to rotate, and one thumbnail at 512px to generate.
    """

    DESTINATION = '/srv/geolib/airphoto_historic/'

    r = models.AerialRun.objects.get(identifier=run)

    for frame in r.frames.all():
        command = "convert " + r.survey


class Airphoto1940_organise():
    """Methods to categorise and catalogue the historic air photo collection.

    Analyse the source directory, which contains over 4,000 files
    downloaded from retrolens in December 2016. This directory
    contains both the medium ('med/') and high ('high') density scans
    of historic aerial photographic surveys. Provide modules to
    extract from the filename of each image:

    -   The survey, run and frame number.
    -   The URL link to the copy held at retrolens.
    """

    SOURCE = '/srv/geolib/downloads/retrolens_2016-12/'
    DESTINATION = '/home/malcolm/tmp/'
    DESTINATION = '/srv/geolib/airphoto_historic/'
    RETROLENS = 'https://files.interpret.co.nz/Retrolens/Imagery/'
    RIGHTS = "Sourced from http://retrolens.nz and licensed by LINZ CC-BY 3.0"

    def __init__(self):
        """ """

    def run_source(self):
        """Iterate the source directory, calling various methods.

        Create a memory structure mapping survey run and frame:

            surveys = {

                'SN155': {
                    'A': {
                        '1':{}, '2',:{} '3':{}...
                     },
                }
            }
        """

        directory = os.path.join(self.SOURCE, 'med/')

        surveys = {}
        commands = ''

        for fname in sorted(os.listdir(directory)):

            (survey, run, frame) = self.survey_run_frame(fname)

            sourcepath_med = os.path.join(directory, fname)
            fname_high = fname.replace('_med', '')
            sourcepath_high = os.path.join(self.SOURCE, 'high/') + fname_high
            dest_survey = os.path.join(self.DESTINATION, 'SN' + survey)
            dest_run = os.path.join(dest_survey, run)
            dest_frame = os.path.join(dest_run, frame)

            frame_struct = {
                'local_fname': fname,
                'retrolens_url': self.get_retrolens_url(survey, run, frame),
                'id': run + '/' + frame,
                'full_id': 'SN' + survey + '/' + run + '/' + frame,
            }

            if not os.path.isdir(dest_survey):
                print "Creating directory", dest_survey
                os.mkdir(dest_survey)
                # commands += 'mkdir ' + dest_survey + '\n'

            if not os.path.isdir(dest_run):
                print "Creating directory", dest_run
                os.mkdir(dest_run)
                # commands += 'mkdir ' + dest_run + '\n'

            if not os.path.isdir(dest_frame):
                print "Creating directory", dest_frame
                os.mkdir(dest_frame)
                # commands += 'mkdir ' + dest_frame + '\n'

            commands += ('cp ' + os.path.join(dest_frame, sourcepath_med) +
                         ' ' + os.path.join(dest_frame, fname) + '\n')
            commands += ('cp ' + os.path.join(dest_frame, sourcepath_high) +
                         ' ' + os.path.join(dest_frame, fname_high) + '\n\n')

            if survey not in surveys.keys():
                print survey
                surveys[survey] = {
                    run: {
                        frame: frame_struct, },
                }

                airsurvey = models.AerialSurvey.objects.create(
                    **self.build_survey_record(survey))
                airsurvey.save()

                airrun = models.AerialRun.objects.create(
                    **self.build_run_record(airsurvey, run))
                airrun.save()

                airframe = models.AerialFrame.objects.create(
                    **self.build_frame_record(airrun, frame))
                airframe.save()

            elif run not in surveys[survey].keys():
                print "    ", run
                surveys[survey][run] = frame_struct

                airrun = models.AerialRun.objects.create(
                    **self.build_run_record(airsurvey, run))
                airrun.save()

                airframe = models.AerialFrame.objects.create(
                    **self.build_frame_record(airrun, frame))
                airframe.save()

            elif frame not in surveys[survey][run].keys():
                print "        ", frame
                surveys[survey][run][frame] = frame_struct

                airframe = models.AerialFrame.objects.create(
                    **self.build_frame_record(airrun, frame))
                airframe.save()

        self.commands = commands
        self.surveys = surveys

    def build_survey_record(self, sn):
        """Produce a dictionary suitable for record creation.

        Requires a string survey number.
        """

        rights = self.RIGHTS
        try:
            ordinal = int(sn)
        except ValueError:
            ordinal = None

        record = {
            'id': 'SN' + sn,
            'ordinal': ordinal,
            'name': None,
            'year_first': None,
            'year_last': None,
            'film_type': 'B&W',
            'rights': rights,
            'comments': None,
            'geom': None,
        }
        return record

    def build_run_record(self, survey, rn):
        """Produce a dictionary suitable for record creation.

        Requires a survey object and a string run number.
        """

        rights = self.RIGHTS

        try:
            ordinal = int(rn)
        except ValueError:
            ordinal = None

        record = {
            'survey': survey,
            'identifier': rn,
            'ordinal': ordinal,
            'direction': None,
            'rights': rights,
            'comments': None,
            'geom': None,
        }

        return record

    def build_frame_record(self, run, fn):
        """Produce a dictionary suitable for record creation.

        Requires a run object and a string frame number. Identifier is
        a string composed of these two numbers separated by a slash.

        """

        rights = self.RIGHTS

        try:
            ordinal = int(fn)
        except ValueError:
            ordinal = None

        record = {
            'run': run,
            'identifier': run.identifier + '/' + fn,
            'source_url': self.get_retrolens_url(
                run.survey.sn(), run.rn(), fn),
            'ordinal': ordinal,
            'date_flown': None,
            'time_flown': None,
            'alt_ft': None,
            'alt_m': None,
            'focal_length': None,
            'aperture': None,
            'status': None,
            'name': None,
            'description': None,
            'provenance': None,
            'rights': rights,
        }

        return record

    def build_file_record(self):
        """ """

        provenance = "Downloaded 2016-12-19 from "

        record = {
            'filename': '',
            'uri': '',
            'file_format': 'jpg',
            'received': datetime.datetime.now(),
            'received_fname': '',
            'uploaded': None,
            'uploaded_by': None,
            'provenance': provenance,
            'notes': None,
            'filetype': '',
        }

        return record

    def survey_run_frame(self, fname):
        """Return a tuple of survey, run, frame numbers for given filename."""

        bits = fname.split('_')
        if len(bits) != 3:
            return ()

        survey = bits[0]
        (run, frame) = bits[1].split('-')

        return (survey, run, frame)

    def get_retrolens_url(self, survey, run, frame):
        """Return string being the address of the original image file."""

        url = self.RETROLENS + 'SN' + survey
        url += '/Crown_' + survey + '_' + run + '_' + frame + '/'
        return url


class Airphoto1940_download():
    """Download image files from retrolens.nz.

    This outpurs WGET commands to a file. It is intended for one time
    use only, and this should be moved to another module, to reflect
    this.

    """

    SURVEYS = [
        {
            'SN': '155',
            'top': 12,
            'name': '',
            'runs': [
                'A', 'B',
            ]
        },
        {
            'SN': '156',
            'top': 9,
            'name': 'Waikato River (Cambridge - Arapuni) 1940',
            'runs': [
                'A', 'B',
            ]
        },
        {
            'SN': '174',
            'top': 27,
            'name': 'Waikato Coal Field 1941',
            'runs': [
                '293', '294', '295', '296', '297',
                '298', '299', '300', '301', '302',
            ]
        },
        {
            'SN': '192',
            'top': 50,
            'name': 'PUKEKOHE - THAMES - LAKE WAIKARE 1942,48,49,52,54',
            'runs': [
                '273', '274', '275', '276', '280', '281',
                '282', '283', '284', '285', '286', '287',
                '288', '289', '290', '291', '292',
            ]
        },
        {
            'SN': '248',
            'top': 35,
            'name': '',
            'runs': [
                '588', '590', '591', '592', '593', '594', '595', '596',
            ]
        },
        {
            'SN': '253',
            'top': 20,
            'name': 'PT. SHEET 55 (TEMPORARY CHART) 1943-44',
            'runs': [
                '621', '622', '623', '624', '625', '626',
                '627', '628', '629', '630', '631',
            ]
        },
        {
            'SN': '255',
            'name': '',
            'top': 85,
            'runs': [
                '697', '698', '699', '700', '701', '702',
                '703', '704', '705', '706', '707', '708',
                '709', '710', '711', '712', '813', '714', '715',
            ]
        },
        {
            'SN': '266',
            'top': 75,
            'name': 'RAGLAN - CAMBRIDGE -OTOROHANGA 1943-44-46-52',
            'runs': [
                '830', '831', '832', '833', '834', '835',
                '836', '837', '838', '839', '840', '841',
                '841', '842', '843', '844', '845', '846',
                '847', '848', '849', '850', '851',
            ]
        },
    ]

    BASE_URL = "https://files.interpret.co.nz/Retrolens/Imagery/"
    DESTINATION = '/srv/geolib/downloads/retrolens_2016-12/'
    FNAME = '/home/malcolm/tmp/download.sh'

    def __init__(self):

        f = open(self.FNAME, 'w')

        for survey in self.SURVEYS:
            for run in survey['runs']:
                for n in range(1, survey['top'] + 1):
                    url = self.BASE_URL + 'SN' + survey['SN']
                    url += '/Crown_' + survey['SN'] + '_' + run
                    url += '_' + str(n)

                    url_high = url + '/High.jpg'
                    url_med = url + '/Med.jpg'

                    get_url_high = 'wget ' + url_high + ' -O '
                    get_url_high += self.DESTINATION + 'high/' + survey['SN']
                    get_url_high += '_' + run + '-' + str(n) + '.jpg'

                    get_url_med = 'wget ' + url_med + ' -O '
                    get_url_med += self.DESTINATION + 'med/' + survey['SN']
                    get_url_med += '_' + run + '-' + str(n) + '_med.jpg'

                    f.write(get_url_high)
                    f.write('\n')
                    f.write(get_url_med)
                    f.write('\n\n')

        f.close()

LETTERS = (
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
)


def sheet_coords(easting, northing, width, height):
    """Given the northwest corner, return the coords for four
    corners of a sheet.

    This comes back as a tuple, containing two tuples:

    (north, east, south, west),
    ((n, e), (n, e), (n, e), (n, e), (n, e))

    The first are integer northings and eastings for the sheet
    extent. The second is a tuple of five (northing, easting)
    tuples, being the closing polygon coords necessary to create a
    geometry object.

    """

    north = northing
    east = easting + width
    south = northing - height
    west = easting

    nw = (easting, northing)
    ne = (easting + width, northing)
    se = (easting + width, northing - height)
    sw = (easting, northing - height)

    return {
        'north': north,
        'east': east,
        'south': south,
        'west': west,
        'coords': (nw, ne, se, sw, nw),
    }


class GenerateNZMS260grid():
    """Populate the table geolib.NZMSgrid.

    Compute a rectangular grid which maps the NZMS260 series
    topographic maps. Those tiles which do not touch an object on the
    Topo50 islands layer are discarded.

    Dependant on having the islands layer populated.

    The NZMS 260 map series is projected NZMG EPS:2200, but the
    resulting table will be converted to NZTM2000 EPSG:2193.

    """

    N = 6790000
    E = 3010000
    S = 5290000
    W = 1970000
    NZMG = 27200
    NZTM = 2193

    WIDTH = 40000
    HEIGHT = 30000

    grid = []

    def __init__(self, commit=False):
        """Populate the self.grid list.

        """

        self.grid = self.generate_grid()

        if commit:
            for tile in self.grid:
                geom = Polygon(tile[1]['coords'], srid=self.NZMG)

                r = models.NZMSgrid(
                    identifier=tile[0],
                    nzms_ymax=tile[1]['north'],
                    nzms_xmax=tile[1]['east'],
                    nzms_ymin=tile[1]['south'],
                    nzms_xmin=tile[1]['west'],
                    geom=geom,

                    nztm_xmax=0,
                    nztm_ymax=0,
                    nztm_xmin=0,
                    nztm_ymin=0,
                )
                # Test for touching an island.
                island = models.Topo50_Island.objects.filter(
                    geom__intersects=r.geom)

                if island.count():
                    r.save()

            self.correct_nztm_coords()

    def correct_nztm_coords(self):

        tiles = models.NZMSgrid.objects.all()
        for tile in tiles:
            tile.nztm_xmax = tile.geom.coords[0][2][0]
            tile.nztm_ymax = tile.geom.coords[0][0][1]
            tile.nztm_xmin = tile.geom.coords[0][0][0]
            tile.nztm_ymin = tile.geom.coords[0][2][1]

            tile.save()

    def generate_grid(self):

        sheets = []
        easting = self.W
        northing = self.N

        id = 'A01'

        for letter in LETTERS:
            for i in range(1, 51):
                id = letter
                if i < 10:
                    id += '0' + str(i)
                else:
                    id += str(i)

                line = [id, ]
                line.append(sheet_coords(
                    easting, northing, self.WIDTH, self.HEIGHT
                ))
                sheets.append(line)
                northing -= self.HEIGHT

            easting += self.WIDTH
            northing = self.N

        return sheets


class GenerateTopo50grid():
    """Populate the table geolib.Topo50Grid.

    This is done by computing a rectangular grid which maps the Topo50
    series topographic maps. Those tiles which do not touch an object
    on the Topo50 islands layer are discarded.

    Dependant on having the islands layer populated.

    """

    W = 1084000
    N = 6234000
    E = 2092000
    S = 4722000
    ORIGIN = 'AS04'
    WIDTH = 24000
    HEIGHT = 36000

    grid = []

    def __init__(self, commit=False):
        """Populate the self.grid list. Defaults to no database change. """

        self.grid = self.generate_grid()

        if commit:
            for tile in self.grid:
                r = models.Topo50grid(
                    identifier=tile[0],
                    nzms_ymax=tile[1]['north'],
                    nzms_xmax=tile[1]['east'],
                    nzms_ymin=tile[1]['south'],
                    nzms_xmin=tile[1]['west'],
                    geom=Polygon(tile[1]['coords']),
                )
                # Test for touching an island.
                island = models.Topo50_Island.objects.filter(
                    geom__intersects=r.geom)
                if island.count():
                    r.save()

    def incriment_id(self, id):

        letters = id[:2]
        number = int(id[2:])
        places = list(id)

        if number == 45:
            number = 4
            letters = self._incriment_letters(letters)
        else:
            number += 1

        if number < 10:
            number = '0' + str(number)
        else:
            number = str(number)

        return letters + number

    def _incriment_letters(self, letters):
        """Return the next letter identifier in the sequence.

        Rows 'BI', 'BO', and 'CI' are ommitted from the Topo50 grid.

        """

        o1 = letters[0]
        o2 = letters[1]

        if o2 == 'Z':
            o2 = 'A'
            o1 = LETTERS[LETTERS.index(o1) + 1]
        # Skip 'I'
        elif o2 == 'H':
            o2 = 'J'
        # Skip 'O'
        elif o2 == 'N':
            o2 = 'P'
        else:
            i = LETTERS.index(letters[1])
            o2 = LETTERS[i + 1]

        return ''.join([o1, o2])

    def generate_grid(self):
        """Iterate from sheet AS04 to sheet CK45, producing
        sheet coords and identifiers.

        NOTE. The line BI is skipped. So is CI.
        """

        sheets = []
        easting = self.W
        northing = self.N
        id = self.ORIGIN

        while northing > self.S:

            while easting < self.E:
                line = [id, ]
                line.append(sheet_coords(
                    easting, northing, self.WIDTH, self.HEIGHT
                ))
                sheets.append(line)
                easting += self.WIDTH
                id = self.incriment_id(id)

            easting = self.W
            northing -= self.HEIGHT

        return sheets


class TopoMaps():
    """Download directories of map images in geotiff format.

    This is code to be used once when setting up the geolibrary for
    the archaeography project. Objects of this class provide tools to
    download and catalogue geographic files from public collections
    held by the Univeristy of Auckland and Land Information New Zealnd
    (LINZ).

    Three user functions, which should really be performed in order:

    1. download

       Go to LINZ, and the University of Auckland, and download the
       GeoTiff collections.

    1. convert_png

       Provide a set of shell commands using the `convert` utility
       (part of imigemagik image manipulation library) to provide a
       set of PNG copies of the TIFF images, at slihtly reduced size,
       for inline display.

    1. catalogue

        Run through the downloaded files and create records in the
        `geolib_topomapindexfile' table, linked to records in the
        topographic map index.


    SOURCES    A list, containing tuples for each collection.
               The tuples contain (series id, url for directory
               containing images)

    Instantiating an object of this class will step through the
    locations in SOURCES, downloading all the .tiff image files found
    there. These will be saved locally in a directory in the
    geolibrary.

    Records in the model geolib.MapIndex will also be affected. For
    Topo50 and NZMS360 maps, the local filename will be added to the
    existing sheet record. For the NZMS1 series, a record will be
    created, containing a rectangular geometry derived from the
    geographic extents encoded in the geotiff file.

    The Topo50 series from LINZ has a diferent link setup for the files.

    NZMS260

        https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_260/geotif/\
                NZMS260_S16_2004_geo.tif
        <a href="NZMS260_C40_1994_geo.tif">NZMS260_C40_1994_geo.tif</a>

    Topo50

        http://topo.linz.govt.nz/Topo50_raster_images/TIFFTopo50/\
               AT25_TIFFv1-02.tif
        <A HREF="/Topo50_raster_images/TIFFTopo50/AV27_TIFFv2-01.tif">
        AV27_TIFFv2-01.tif</A>

    """

#   Public locations for the geotiff files from each map series.
    SOURCES = [
        ('nzms1',
         'https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_001/geotif/'),
        ('nzms260',
         'https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_260/geotif/'),
        ('topo50',
         'http://topo.linz.govt.nz/Topo50_raster_images/GeoTIFFTopo50/'),
    ]

    DEST = os.path.join(settings.STATICFILES_DIRS[0], 'geolib',)

    def __init__(self):
        """Setup."""

    def catalogue(self):
        """Catalogue the file collection.

        This involves stepping through each of the source directories
        and finding GeoTIFF files.

        For each file, find the sheet, and the sheet record it represents.

        For each file, create a record in the TopoMapsFiles table,
        linked to the sheet record.

        """

        commands = ''
        for source in self.SOURCES:
            self._catalogue_series(source)

        self.commands = commands

    def convert_png(self):
        """Return a string of shell commands to create view copies of tiffs.

        Unfinished.
        """

        commands = ''
        for source in self.SOURCES:

            path_from = os.path.join(
                settings.STATICFILES_DIRS[0], 'geolib/map_', source[0],
            )
            path_to = os.path.join(
                settings.STATICFILES_DIRS[0], 'geolib/map_', source[0],
                'view'
            )

            command = "convert -quiet -resize 2048x2048 " + path_from + " "
            command += path_to + '\n'

            commands += command

        return commands

    def download(self):
        """Iterate the sources, downloading TIFF image files."""

        for source in self.SOURCES:
            destdir = os.path.join(self.DEST, 'map_' + source[0])

            dir = self._read_directory(source[1])

            for item in dir:
                address = source[1] + item
                destpath = os.path.join(destdir, item)

                if os.path.isfile(destpath):
                    print "FOUND", item
                else:
                    print "DOWNLOADING", item
                    r = requests.get(address)
                    with open(destpath, 'wb') as handle:
                        handle.write(r.content)

    def _catalogue_series(self, source):
        """Iterate through the series directory

        NZMS001_N10_1965_geo.tif
        NZMS260_A45_1995_geo.tif
        AW26_GeoTifv2-03.tif


        """

        print "_catalogue_series", source

        commands = ''
        directory = os.path.join(self.DEST, 'map_' + source[0])
        notfound = []
        sheet = None

#       Files for which records can't be found automatically.
        specials = {
            'C40-D40': 'D40 & Pt.C40',
            'C40': 'B41, C41 & Pt. C40',
            'P26-Q26-inset': 'Q26 & Pt. P26',
            'P26-Q26': 'Q26 & Pt. P26',
            'Q27-R27-28': 'R27, R28 & Pt. Q27',
            'Q27-R27': 'R27, R28 & Pt. Q27',
            'R06': 'R06, R07 & S07',
            'R07': 'R06, R07 & S07',
            'R25-26': 'Pt. R25 & R26',
            'R25-S25': 'S25 & Pt. R25',
            'S11-T11': 'T11 & Pt. S11',

            'BA36': 'BA36ptBA35',
            'BD40': 'BD40ptBE40',
            'CH05CH06': 'CH05/CH06',
            'CJ07CK07': 'CJ07/CK07',
        }

        if not os.path.isdir(directory):
            return None

        allframes = 0
        for fname in sorted(os.listdir(directory)):
            if '.tif' in fname:
                allframes += 1
                library = '/srv/geolib/map_' + source[0]
                series = source[0].upper()
                uri = os.path.join(source[1], fname)

                path_from = os.path.join(library, fname)
                (basename, ext) = os.path.splitext(fname)
                path_to = os.path.join(library, 'view', basename + '.png')
                bits = fname.split('_')

                if source[0] == 'topo50':
                    sheet_id = bits[0]
                    sheet_id = sheet_id.replace('pt', '')
                    provenance = "Downloaded from LINZ, 2018."
                else:
                    sheet_id = bits[1]
                    provenance = "Downloaded from "
                    provenance += "Auckland Unversity public server, 2018."

#               First try at the index record. Is it a simple sheet_id?
                try:
                    sheet = models.TopoMap.objects.get(
                        series_id=source[0].upper(), sheet_id=sheet_id)

                except models.TopoMap.MultipleObjectsReturned:
                    print "MULTIPLE OBJECTS RETURNED"

                except models.TopoMap.DoesNotExist:
                    parts = sheet_id.split('-')
                    sheet = models.TopoMap.objects.filter(
                        series_id=source[0].upper(),
                        sheet_id__contains=parts[0])
                    if sheet.count() > 0:
                        sheet = sheet[0]
                    elif sheet.count() == 0:
                        sheet = None
#                    try:
#                        sheet = models.TopoMap.objects.get(
#                            series_id=source[0].upper(),
#                            sheet_id__contains=parts[0])
#                    except models.TopoMap.DoesNotExist:
#                        if sheet_id not in notfound:
#                            notfound.append(sheet_id)
#                    except models.TopoMap.MultipleObjectsReturned:
#                        if sheet_id not in notfound:
#                            notfound.append(sheet_id)
#               Deal with the exceptions -- unfound sheets.
                if not sheet:
                    if sheet_id in specials.keys():
                        sheet = models.TopoMap.objects.get(
                            series_id=source[0].upper(),
                            sheet_id=specials[sheet_id]
                        )
                if not sheet:
                    print "NO SHEET", sheet_id
                else:
                    # Build the file record.
                    now = datetime.datetime.now(pytz.utc)
                    try:
                        filerec = models.TopoMapFile.objects.get(
                            filename=fname)
                        print "existing record for file", filerec
                    except models.TopoMapFile.DoesNotExist:
                        filerec = models.TopoMapFile(
                            sheet=sheet,
                            filename=fname,
                            uri=uri,
                            file_format='GeoTIFF',
                            received=now,
                            received_fname=fname,
                            provenance=provenance,
                        )
                        filerec.save()
                        print "creating record for file", filerec

        return commands

    def _read_directory(self, dir):
        """Return a list of filenames, which can be downloaded with wget.

        Return the filenames only. The calling function supplies the
        URL to the directory.

        """

        files = []
        print "LISTING", dir
        s = requests.get(dir)

        soup = BeautifulSoup(s.text, 'html.parser')

        for link in soup.findAll('a'):
            if '.tif' in link['href']:
                # Special correction for the Topo50 collection.
                line = link['href'].replace(
                    '/Topo50_raster_images/GeoTIFFTopo50/', '')
                files.append(line)

        return files
