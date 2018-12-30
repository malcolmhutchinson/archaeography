"""Scrape archaeological data from online"""

import datetime
import hashlib
import mechanize
import os
import pytz
import re

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point

import settings
import models
from geolib.models import Region, TerritorialAuthority
import datamap


class Scrape(BaseCommand):
    """Command to extract archaeological records from NZAA's ArchSite.

    Initialise an object of this class with a list of NZAA
    identifiers, one or many. On receipt of this list, the program
    calls scrape_this(), which processes the string into a Python
    list, and then calls scrape_site() on each NZAA identifier on the
    input list.

    The method scrape_site() does everything else for an individual
    record. This is documented in its docstring.

    """

    LOGIN_PAGE = settings.LOGIN_PAGE
    SITE_PAGE = settings.SITE_PAGE

    # You must have your own Archsite Login, in
    # secrets.py. See the comment in nzaa/settings.py.
    USERNAME = settings.LOGIN_ARCHSITE['default'][0]
    PASSWORD = settings.LOGIN_ARCHSITE['default'][1]

    DOWNLOADS = settings.BASE_FILESPACE
    LOCALOG = os.path.join(settings.BASE_DIR, 'etc')
    LOGFILE = 'scrape_'
    LOGFILE += str(datetime.datetime.date(datetime.datetime.now()))[:7]
    LOGFILE += '.log'
    LOGFILENAME = os.path.join(LOCALOG, LOGFILE)
    RECORD_PRESENT = False
    VERBOSE = False

    browser = None
    connection = False
    extract = None

    def __init__(self, identifiers=False, files=False, verbose=False):
        """Accept a list of NZAA identifier strings.

        The files flag, when set True, will force the use of the
        selenium plugin to drive a firefox browser. In addition to
        parsing the electronic elements of a record, it will also
        attempt to download copies of files held on ArchSite. This is
        necessary to interpret the JavaScript used by ArchSite to list
        files associated with a record. This function hasn't been
        written yet!

        """

        self.identifiers = identifiers
        self.VERBOSE = verbose
        self.files = files

        targets = []
        if not os.path.isdir(self.LOCALOG):
            os.makedirs(self.LOCALOG)

        if identifiers:
            targets = self.scrape_this(identifiers, verbose)

        self.f = open(self.LOGFILENAME, 'a')
        for target in targets:
            self.scrape_site(target)
        self.f.close()

    def logging(self, log):
        """Write a line to a log file, recording scrape activity.

        Writes to self.f, a file object which will have been opened
        before a series of scrape site events.

        """

        now = datetime.datetime.now(pytz.utc)
        timestamp = unicode(now.replace(microsecond=0))

        line = '\t'.join((timestamp, log)) + '\n'

        try:
            self.f.write(line)
        except ValueError:
            logfile = self.LOGFILENAME
            f = open(logfile, 'a')
            f.write(line)
            f.close()

        return True

    def scrape_this(self, identifiers, verbose=False):
        """Return a list of nzaa_id values.

        Taking the input list identifiers, keep splitting it down by
        sending it to functions until you are reduced to a list of
        individual nzaa identifiers.

        """

        if verbose:
            print "Scrape this", identifiers

        targets = []
        p = re.compile(r'^([A-Za-z]\d{2}/\d+)')

        for item in identifiers:
            if item in settings.NZMS260:
                if verbose:
                    print "Scraping sheet", item
                targets.extend(self.find_sheet_members(item))
            else:
                q = p.match(item)
                if q:
                    targets.append(q.group())

        return targets

    def find_sheet_members(self, sheet, plus=50):
        """Given a sheet number, return a list of targets. """

        if self.VERBOSE:
            print "find_sheet_numbers", sheet

        targets = []

        s = models.Site.objects.filter(nzms_sheet=sheet).order_by('-ordinal')
        if s.count() > 0:
            highest = s[0].ordinal + plus
        else:
            highest = plus

        for n in range(1, highest):
            targets.append(sheet + "/" + str(n))

        return targets

    def scrape_site(self, nzaa_id):
        """All the functions to update a site record.

        Login to ArchSite (if necessary). Go to the record, get the
        source, process this into an extract, then process this into
        the site record structures.

        Extract values for actor, feature and period. If no record for
        each value is found, create one and add this site to it's
        relations table.

        Compute an MD5 checksum for the values and compare this with
        the stored version.

        Check for the existence of a site record, and an update0 record.

        Save the records into the db apopropriately.

        """

        message = "Scraping site " + nzaa_id
        if self.VERBOSE:
            print message

        s = None
        u = None
        update_id = nzaa_id + '-0'
        html = None
        extract = None

        now = datetime.datetime.now(pytz.timezone('NZ'))
        unchanged = False

        if self.login():
            html = self.visit_site(nzaa_id)
            if html:
                extract = self.extract_values(html)

        if not extract:
            message = "No site record found for " + nzaa_id
            if self.VERBOSE:
                print message
            return None

        self.extract = extract

#       Create MD5 checksum of extracted values, replacing unknown
#       unicode characters.
        hash = hashlib.md5()
        checksum = ''
        for k in sorted(extract.keys()):
            try:
                hash.update(
                    unicode(extract[k])
                    .replace(u'\u0101', '&#x0101;')
                    .replace(u'\u012b', '&#x012b;')
                    .replace(u'\u016b', '&#x016b;')
                    .replace(u'\u02bc', '&#x02bc;')
                    .replace(u'\u02c6', '&circ;')
                    .replace(u'\u02da', '&#x02da; ')
                    .replace(u'\u2013', '&ndash;')
                    .replace(u'\u2014', '&mdash;')
                    .replace(u'\u2018', '&lsquo;')
                    .replace(u'\u2019', '&rsquo;')
                    .replace(u'\u201c', '&ldquo;')
                    .replace(u'\u201d', '&rdquo;')
                    .replace(u'\u2022', '&bull;')
                    .replace(u'\u2026', '&hellip;')
                    .replace(u'\u20a4', '&#x20a4;')
                    .replace(u'\u2154', '&#x2154;')
                    .replace(u'\uf644', '')
                    .replace(u'\uf64b', '')
                    .replace(u'\uf64c', '')
                    .replace(u'\xa0', '&nbsp;')
                    .replace(u'\xa3', '&pound;')
                    .replace(u'\xa9', '&copy;')
                    .replace(u'\xac', '&not;')
                    .replace(u'\xad', '&shy;')
                    .replace(u'\xb0', '&deg;')
                    .replace(u'\xb1', '&plusmn;')
                    .replace(u'\xb2', '&sup2;')
                    .replace(u'\xb3', '&sup3;')
                    .replace(u'\xb4', '&acute;')
                    .replace(u'\xb7', '&middot;')
                    .replace(u'\xba', '&ordm;')
                    .replace(u'\xbc', '&frac14;')
                    .replace(u'\xbd', '&frac12;')
                    .replace(u'\xbe', '&frac34;')
                    .replace(u'\xe6', '&aelig;')
                    .replace(u'\xe7', '&ccedil;')
                    .replace(u'\xe8', '&egrave;')
                    .replace(u'\xe9', '&eacute;') +
                    "\n"
                )
            except UnicodeEncodeError as e:
                line = nzaa_id + " " + str(e) + "\n"
                dumpfile = "/home/malcolm/tmp/scrape_dumps.txt"
                f = open(dumpfile, "a")
                f.write(line)
                f.close

        digest = hash.hexdigest()

#       Build the structures necessary to affect database tables.
        (new_site, site, update0) = self.process_extract(extract)

#       Try finding a site record.
        try:
            s = models.Site.objects.get(nzaa_id=nzaa_id)
            if digest == s.digest:
                unchanged = True
                s.extracted = now
                message = ("Record unchanged since " +
                           unicode(s.last_change.replace(microsecond=0))
                           )
                log = (
                    '127.0.0.1', 'scrape',
                    message,
                )
                if self.VERBOSE:
                    print message

            else:
                message = "Updating existing site record for " + nzaa_id
                s.digest = digest
                s.last_change = now
                self.logging(message)
                if self.VERBOSE:
                    print message

                log = (
                    '127.0.0.1', 'scrape',
                    "Updating record from from ArchSite."
                )
                s.__dict__.update(**site)

        except models.Site.DoesNotExist:
            message = "Creating site record for " + nzaa_id
            self.logging(message)
            if self.VERBOSE:
                print message
            data = new_site.copy()
            data.update(new_site)
            s = models.Site(**data)

            s.created = datetime.datetime.now(pytz.utc)
            s.created_by = 'scrape'
            s.digest = digest
            s.last_change = now

            log = (
                '127.0.0.1', 'scrape',
                "Creating record from from ArchSite.",
            )

            point = Point(s.easting, s.northing, 2913)
            if not s.region:
                s.region = s.get_region()

            if not s.tla:
                s.tla = s.get_tla()

            if not s.island:
                s.island = s.get_island()

            if self.VERBOSE:
                print "Saving site record", s

        s.save(log=log)

#       If there are no changes, then we have done all we have to do.
        if unchanged:
            return None

#       Deal with actors.
        sourcenames = s.list_actors()
        for sourcename in sourcenames:
            try:
                a = models.Actor.objects.get(sourcename=sourcename)
            except:
                a = models.Actor(sourcename=sourcename)
                a.save()
            a.sites.add(s)
#       Deal with features.
        features = s.list_features()
        if features:
            for feature in features:
                try:
                    f = models.Feature.objects.get(name=feature)
                except:
                    f = models.Feature(name=feature)
                    f.save()
                f.sites.add(s)
#       Deal with period.
        periods = s.list_periods()
        for period in periods:
            try:
                p = models.Periods.objects.get(name=period)
            except models.Periods.DoesNotExist:
                p = models.Periods(name=period)
                p.save()
            p.sites.add(s)

        update0['site'] = s
        update0['update_id'] = update_id

        try:
            u = models.Update.objects.get(update_id=update_id)
            u.nzaa_id = s
            message = "Updating existing record for " + update_id
            self.logging(message)
            if self.VERBOSE:
                print message
            u.__dict__.update(**update0)

        except models.Update.DoesNotExist:
            message = "Creating update record for " + update_id
            self.logging(message)
            if self.VERBOSE:
                print message
            u = models.Update(**update0)
            u.nzaa_id_id = s
            u.created = datetime.datetime.now(pytz.utc)
            u.created_by = 'scrape'

        u.save(log=log)

    def login(self):
        """Provide an authenticated browser session.

        This uses the headless browser mechanize as default. If files
        need to be downloaeds, the selenium module to command a
        Firefix browser will be required.

        """

        if self.connection:
            return True

        message = "Attempting to login to archsite"
        if self.VERBOSE:
            print message

        browser = mechanize.Browser()
        browser.open(self.LOGIN_PAGE)

        browser.select_form(nr=0)
        browser.form['UserName'] = self.USERNAME
        browser.form['Password'] = self.PASSWORD

        response = browser.submit()

        if "<h2>Log in</h2>" in response.read():
            self.connection = False
            message = "Login Failed"
            self.logging(message)
            if self.VERBOSE:
                print message
            return None

        self.connection = True
        message = "Logged in as " + self.USERNAME
        self.logging(message)
        if self.VERBOSE:
            print message

        self.browser = browser
        return True

    def visit_site(self, nzaa_id):
        """Return the HTML code for site page on ArchSite.
        """

        message = "Visiting " + nzaa_id
        if self.VERBOSE:
            print message

        if not self.connection:
            self.login()

        if not self.connection:
            message = "No connection found. Exiting site page."
            self.logging(message)
            if self.VERBOSE:
                print message

            return None

        browser = self.browser
        url = self.SITE_PAGE + nzaa_id

        try:
            page = browser.open(url)

            return page.read()

        except:
            self.logging("Internal error" + url)
            return None

    def extract_values(self, html):
        """Return a dictionary of field: value items from an ArchSite page.
        """

        if "No data was found for the site" in html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        try:
            nzaa_id = soup.find_all('h3')[1].contents[1].strip()
        except:
            return None

        try:
            nzms_id = soup.find_all('h3')[1].contents[3].strip()
        except:
            nzms_id = None

        try:
            evidence = (soup.find('dt', text='Evidence site destroyed')
                        .findNextSibling('dd').text.strip())
        except:
            evidence = None

#       The extracted values. Adding or removing fields, from this
#       structure will affect the MD5 checksum used to determine if a
#       site record has changed.
        record = {
            "nzaa_id": nzaa_id,
            "nzms_id": nzms_id,
            "evidence": unicode(evidence),
            "status": unicode(soup.find('h4').text),
            "short_desc": unicode(soup.find('h4').findNextSibling('p').text),
            "inspected": unicode(soup.find('dt', text='Site inspected by')
                                 .findNextSibling('dd').text),
            "nztm_coords": unicode(soup.find('dt', text='NZTM Coordinates')
                                   .findNextSibling('dd').text),
            "source": unicode(soup.find('dt', text='Source of spatial data')
                              .findNextSibling('dd').text.strip()),
            "finder_aid": unicode(soup.find('dt', text='Finder Aid')
                                  .findNextSibling('dd').text.strip()),
            "type": unicode(soup.find('dt', text='Site Type')
                            .findNextSibling('dd').text.strip()[:254]),
            "features": unicode(soup.find('dt', text='Features')
                                .findNextSibling('dd').text.strip()[:2048]),
            "description": unicode(soup.find('dt', text='Description')
                                   .findNextSibling('dd').prettify()),
            "site_name": unicode(soup.find('dt', text='Name')
                                 .findNextSibling('dd').text.strip()[:254]),
            "ethnicity": unicode(soup.find('dt', text='Ethnicity')
                                 .findNextSibling('dd').text.strip()[:254]),
            "period": unicode(soup.find('dt', text='Period')
                              .findNextSibling('dd').text.strip()[:254]),
            "assoc_sites": unicode(soup.find('dt', text='Associated Sites')
                                   .findNextSibling('dd').text.strip()[:2048]),
            "condition": unicode(soup.find('dt', text='Condition')
                                 .findNextSibling('dd').text.strip()),
            "condition_notes": unicode(soup.find('dt', text='Condition Notes')
                                       .findNextSibling('dd').prettify()),
            "landuse": unicode(soup.find('dt', text='Land Use')
                               .findNextSibling('dd').text.strip()[:254]),
            "threats": unicode(soup.find('dt', text='Threats')
                               .findNextSibling('dd').text.strip()[:254]),
        }
        if record['inspected'] == ' on ':
            record['inspected'] = None

        message = "Parsed ArchSite page content for " + record['nzaa_id']
        if self.VERBOSE:
            print message

        return record

    def process_extract(self, extract):
        """Process the extracted dictionary into fields for db injection

        """

        message = "Processing extract for " + extract['nzaa_id']
        if self.VERBOSE:
            print message

        nzaa_id = extract['nzaa_id']
        coords = extract['nztm_coords'].split(' ')
        easting = int(coords[1])
        northing = int(coords[3])

        visited_by = ''
        visited = ''
        if extract['inspected']:
            visited_by, visited = extract['inspected'].split(' on ')

        if not len(visited):
            visited = None
        if not len(visited_by):
            visited_by = None

        if visited:
            visited = datetime.datetime.strptime(visited, '%d/%M/%Y')
            visited = unicode(visited)[0:10]

        raw_list = extract['assoc_sites'].split('\n')
        assoc_list = []
        for item in raw_list:
            if len(item) > 0:
                assoc_list.append(item.strip())
        associated_sites = ", ".join(assoc_list)

        now = datetime.datetime.now()
        user = os.getlogin()
        timestamp = unicode(now.replace(microsecond=0))

        provenance = "Downloaded " + timestamp + " From ArchSite  \n"
        provenance += "https://nzaa.eaglegis.co.nz/NZAA/Site/?id=" + nzaa_id

        sheet, ordinal = nzaa_id.split('/')
        site_ordinal = int(ordinal)

        site_type, site_subtype = datamap.map_type(extract)
        period = datamap.map_period(extract)
        ethnicity = datamap.map_ethnicity(extract)

        condition = self.from_archsite(extract['condition_notes']).strip()

        description = extract['short_desc'] + "\n\n"
        description += self.from_archsite(extract['description'])

        reference = None
        rights = None

        new_site = {
            'ordinal': site_ordinal,
            'site_name': extract['site_name'],
            'other_name': None,
            'site_type': site_type,
            'site_subtype': site_subtype,
            'location': None,
            'period': period,
            'ethnicity': ethnicity,
            'landuse': extract['landuse'],
            'threats': extract['threats'],
            'features': extract['features'],
            'associated_sites': associated_sites,
            'visited': visited,
            'visited_by': visited_by,
            'easting': easting,
            'northing': northing,
            'geom': Point(easting, northing, srid=2193),
            'geom_poly': None,
            'created': datetime.datetime.now(pytz.utc),
            'created_by': 'scrape',
            'modified': datetime.datetime.now(pytz.utc),
            'modified_by': 'scrape',
            'accessioned': datetime.datetime.now(pytz.utc),
            'accessioned_by': 'malcolm',
            'provenance': provenance,
            'extracted': datetime.datetime.now(pytz.utc),
            'lgcy_assocsites': extract['assoc_sites'],
            'lgcy_capmethod': extract['source'],
            'lgcy_condition': extract['condition'],
            'lgcy_ethnicity': extract['ethnicity'],
            'lgcy_evidence': extract['evidence'],
            'lgcy_inspected': extract['inspected'],
            'lgcy_landuse': extract['landuse'],
            'lgcy_period': extract['period'],
            'lgcy_shortdesc': extract['short_desc'],
            'lgcy_status': extract['status'],
            'lgcy_features': extract['features'],
            'lgcy_threats': extract['threats'],
            'lgcy_type': extract['type'],
            'lgcy_easting': easting,
            'lgcy_northing': northing,

            'nzaa_id': nzaa_id,
            'nzms_id': extract['nzms_id'],
            'nzms_sheet': sheet,
            'tla': None,
            'region': None,
            'island': None,
            'recorded': None,
            'recorded_by': None,
            'updated': None,
            'updated_by': None,
            'record_quality': None,
            'assessed': None,
            'assessed_by': None,
        }
        site = {
            'easting': easting,
            'northing': northing,
            'nzms_id': extract['nzms_id'],
            'lgcy_assocsites': extract['assoc_sites'],
            'lgcy_capmethod': extract['source'],
            'lgcy_condition': extract['condition'],
            'lgcy_ethnicity': extract['ethnicity'],
            'lgcy_evidence': extract['evidence'],
            'lgcy_inspected': extract['inspected'],
            'lgcy_landuse': extract['landuse'],
            'lgcy_period': extract['period'],
            'lgcy_shortdesc': extract['short_desc'],
            'lgcy_status': extract['status'],
            'lgcy_features': extract['features'],
            'lgcy_threats': extract['threats'],
            'lgcy_type': extract['type'],
            'lgcy_easting': easting,
            'lgcy_northing': northing,
            'status': extract['status'].replace('Status ', ''),
            'extracted': datetime.datetime.now(pytz.utc),
        }
        update0 = {
            'ordinal': 0,
            'update_type': 'Legacy',

            'site_name': extract['site_name'],
            'other_name': None,
            'site_type': site_type,
            'site_subtype': site_subtype,
            'location': None,
            'period': period,
            'ethnicity': ethnicity,
            'landuse': extract['landuse'],
            'threats': extract['threats'],
            'features': extract['features'],
            'associated_sites': associated_sites,
            'visited': visited,
            'visited_by': visited_by,
            'easting': easting,
            'northing': northing,
            'geom': Point(easting, northing, srid=2193),
            'geom_poly': None,
            'modified': datetime.datetime.now(pytz.utc),
            'modified_by': 'scrape',
            'accessioned': None,
            'accessioned_by': None,
            'provenance': provenance,
            'extracted': datetime.datetime.now(pytz.utc),

            'introduction': None,
            'finder_aid': extract['finder_aid'],
            'description': description,
            'condition': condition,
            'references': reference,
            'rights': rights,
            'update_note': None,
            'updated': None,
            'updated_by': None,
            'status': 'Approved',
            'opstatus': None,
            'owner': None,
        }

        return new_site, site, update0

    def parse_listfile(self, filename):
        """Return a list of nzaa_id values from a file."""

        if not os.path.isfile(filename):
            return None

        record_list = []
        f = open(filename, 'r')

        for line in f:
            if not line[0] == '#':
                line = line.replace('\n', '')
                record_list.extend(line.split(' '))

        return record_list

    # Needs a better name.
    def from_archsite(self, content):
        """Cleans unwanted html tags."""

        content = content.replace('<dd>', '')
        content = content.replace('</dd>', '')

        if '<br/>' in content:
            content = content.replace('\n', '')
            content = content.replace('<br/>', '\n')

        return content

    # Legacy code. Possibly depreciated.
    def site_or_sheet(self, item):
        if item in settings.NZMS260:
            return 'site'

        parts = item.split('/')
        if not len(parts) == 2:
            return 'none'

        if not parts[0] in settings.NZMS260:
            return 'none'

        try:
            ordinal = int(parts[1])
        except ValueError:
            return 'none'

        return 'site'
