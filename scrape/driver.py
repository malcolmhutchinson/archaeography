"""Driver for the scrape application.

This module contains code developed to run once, to produce a
product. Once the library tables are populated and errors have been
detected and corrected, there will be no further use for it.

Because this starts off as a command-line thing, it has no views. But
I need a place to collect the code to upload data from CSV files, and
to call the methods which process those data into the library tables.

This stuff will be called initially from the Djamgo shell, and then
from the manage.py command.

"""

import os
import csv
import scrape.models as models
import archlib.models
import codecs
import urllib2
from bs4 import BeautifulSoup


class HNZ():

    def insert_issues(self):
        pubid = 'NZHPT'
        number = 1
        volume = 1
        p = archlib.models.Publication.objects.get(id=4)
        for n in range(1958, 2016):
            identifier = pubid + '/' + str(volume)
            pub_date = str(n) + '-01-01'
            i = archlib.models.Issue(
                publication=p,
                identifier=identifier, volume=volume, number=number,
                pub_date=pub_date,
            )
            i.save()
            volume += 1
            print "inserting ", identifier

    def injection(self):

        h = models.HertNZ.objects.all()
        for j in h:
            p = archlib.models.Paper(
                issue=j.issue,
                category='report',
                title=j.title,
                source_id=j.report_id,
                )
            p.save()
            for arch in j.archaeologists:
                p.author.add(arch)


class AINZlinks():

    issues = None

    def __init__(self):
        self.issues = archlib.models.Issue.objects.filter(publication__id=1)

    def find_directories(self):
        """Using the directory predictor in the Issue class, find those issues
        which have a directory listing on the NZAA webite.
        """

        for i in self.issues:
            print i.id, i.guess_directory_url()

    def get_dir_listing(self, index):

        targets = []
        response = urllib2.urlopen(self.issues[index].guess_directory_url())
        html = response.read()

        soup = BeautifulSoup(html, 'html.parser')

        for anchor in soup.find_all('a'):
            if ('AINZ' in anchor.get('href') and
                    '.pdf' in anchor.get('href').lower()):
                targets.append(anchor.get('href'))

        for target in targets:
            fields = self._fields_from_filename(target)

            rec = archlib.models.Paper.objects.filter(issue__publication=1)
            rec = rec.filter(
                issue__volume=fields['volume'],
                issue__number=fields['number'],
                # page_first=fields['page_first'],
            )

    def _fields_from_filename(self, filename):
        """Return the volume, number and pages from a filename."""

        digits = (
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-',
        )

        fields = {
            'volume': 0,
            'number': 0,
            'page_first': 0,
            'page_last': 0,
            'author': '',
            'filename': filename,
        }

        filename = filename.replace('AINZ', '')

        parts = filename.split('.')
        fields['volume'] = int(parts[0])
        fields['number'] = int(parts[1])

        chunk = parts[2]
        index = 0
        for letter in chunk:
            if letter in digits:
                index += 1
            else:
                break

        pages = chunk[:index]
        parts = pages.split('-')
        fields['page_first'] = int(parts[0])
        if len(parts) > 1:
            fields['page_last'] = int(parts[1])
        else:
            fields['page_last'] = int(parts[0])

        return fields

    def update_links(self):

        links = models.AINZlinks.objects.all()
        for link in links:
            if link.paper:
                paper = archlib.models.Paper.objects.get(id=link.paper.id)
                paper.source = link.source
                paper.save()


class ScrapeAINZ():
    """Retrieve the url links to PDF documents.
    """

    INDEX = None

    def __init__(self):

        self.INDEX = "http://nzarchaeology.org/cms/index.php/"
        self.INDEX += "publications/34-ainz/114-ainz-downloads"


class NZJA():
    """Transform the data from NZJAcontents table into archlib.papers.
    """

    def __init__(self):

        self.url = "http://nzarchaeology.org/cms/index.php/publications/"
        self.url += "91-new-zealand-journal-of-archaeology-nzja"
        self.j = archlib.models.Publication.objects.get(identifier='NZJA')

    def inject_papers(self):
        """"From the NZJAcontents table, create records in paper table.
        """
        issue = None
        c = models.NZJAcontents.objects.all()

        for record in c:

            identifier = 'NZJA/' + str(record.volume)
            i = archlib.models.Issue.objects.filter(
                identifier=identifier,
            )

            if len(i) == 1:
                issue = i[0]

            p = archlib.models.Paper(
                category='article',
                pub_issue=issue,
                title=record.title,
                pub_date=record.pub_date,
                source=record.link,
            )

            p.save()
            for archaeologist in record.archaeologists:
                p.author.add(archaeologist)

    def find_archs(self):
        """Iterate through scrape.NZJAcontents recoords.
        """

        c = models.NZJAcontents.objects.all()
        archaeologists = []
        not_recognised = []

        for record in c:
            (a, b) = record.archaeologists
            archaeologists.extend(a)
            not_recognised.extend(b)

        print len(archaeologists), " archaeologists."
        print len(not_recognised), " not recognised."

        return archaeologists, set(sorted(not_recognised))

    def create_issues(self):
        year = 1979
        for n in range(1, 31):
            pub_date = str(year) + '-01-01'
            identifier = 'NZJA/' + str(n)
            issue = archlib.models.Issue(
                publication=self.j,
                identifier=identifier,
                volume=n,
                number=1,
                pub_date=pub_date,
            )
            year += 1
            issue.save()


class Articles():
    """Extract the links to author and issue from the AINZ index.
    """

    def __init__(self):

        index = models.AINZindex.objects.all()
        count = 0
        found = 0
        notfound = 0
        multiple = 0
        totalrec = 0
        unfound_auntors = []
        i = None

        for item in index:
            count += 1
            try:
                i = archlib.models.Issue.objects.get(identifier=item.g)

            except archlib.models.Issue.DoesNotExist:
                print "Issue not found", item.cite

            p = archlib.models.Paper(
                category='article',
                pub_issue=i,
                title=item.title,
                pub_date=i.pub_date,
                notes=item.author,
                page_first=item.pageFirst,
                page_last=item.pageLast,
            )
            totalrec += 1
            p.save()

            for author in item.authors_list:
                q = archlib.models.Archaeologist.objects.filter(
                    name_last=author[0], name_first__contains=author[1])

                if len(q) == 0:
                    q = archlib.models.Archaeologist.objects.filter(
                        name_last=author[0], initials__contains=author[1])

                if len(q) == 0 and len(author[0]) != 0:
                    notfound += 1

                elif len(q) > 1:
                    multiple += 1

                elif len(q) == 1 and len(author[0]) > 0:
                    found += 1
                    print q[0]
                    p.author.add(q[0])
                    p.save()

        print "Article records:", totalrec
        print "Found an author record:", found
        print "Not found:", notfound
        print "Found more than one record:", multiple
        print "Total:", found + notfound + multiple


class AINZissues():
    """Extract a list of publications and their issues from the AINZ index.
    """

    articles = None

    def __init__(self):
        """ """

        issues = []

        index = models.AINZindex.objects.all()
        for item in index:
            cut1 = item.cite.split(' ')
            issue = cut1[0].replace(':', '')
            issues.append((issue, item.pub_year))

        self.issues = set(issues)

        p = archlib.models.Publication.objects.get(identifier='AINZ')

        for item in sorted(self.issues):
            identifier = item[0]
            split1 = identifier.split('(')
            volume = int(split1[0])
            number = int(split1[1].replace(')', ''))
            year = item[1]
            if volume == 35 and number == 1:
                year = '1992'
            if year == 'Editorial':
                year = '1967'

            if number == 39:
                number = 4

            if number == 1:
                month = '03'
            elif number == 2:
                month = '06'
            elif number == 3:
                month = '09'
            elif number == 4:
                month = '12'

            pub_date = year + '-' + month + '-01'
            print volume, number, pub_date

            i = archlib.models.Issue(
                identifier=identifier,
                publication=p,
                volume=volume,
                number=number,
                pub_date=pub_date,
            )
            i.save()


class Authors():
    """Extract a list of authors from the sources.
    """

    def __init__(self):
        """
        """

        authors = []
        contents = models.AINZcontents.objects.all()
        for item in contents:
            authors.extend(item.authors_list)

        index = models.AINZindex.objects.all()
        for item in index:
            authors.extend(item.authors_list)

        reports = models.HertNZ_digitalLibCat.objects.all()
        for item in reports:
            authors.extend(item.authors_list)

        l = len(authors)
        authors = set(authors)
        authors = sorted(list(authors))

        output = '/home/malcolm/tmp/names.csv'
        f = codecs.open(output, mode='w', encoding='utf-8')
        f.write("Last name, First name\n")
        for author in authors:
            if author:
                print "Author:", author[0] + "," + author[1]
                f.write(author[0] + "," + author[1] + '\n')


class Importer():
    """Take a csv file, select its destination, and import it into tables.
    """

    def __init__(self, filename):
        """
        """

        if not os.path.isfile(filename):
            raise self.FileNotFound(filename)

        records = []

        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                records.append(row)

        if records[0][0] == 'Author':
            self.insert_contents(records[1:])
        if records[0][0] == 'Volume':
            self.insert_index(records[1:])
        if records[0][0] == 'Report Identifier':
            self.insert_reports(records[1:])

    class FileNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def insert_contents(self, records):

        for record in records:
            author = record[0]
            year = record[1]
            title = record[2]
            citation = record[3]

            try:
                c = models.AINZcontents.objects.get(
                    author=author,
                    year=year,
                    title=title,
                    citation=citation
                )
                c.author = author
                c.year = year
                c.title = title
                c.citation = citation

            except:
                c = models.AINZcontents(
                    author=author,
                    year=year,
                    title=title,
                    citation=citation
                )
            c.save()

        return 0

    def insert_index(self, records):

        for record in records:
            volume = record[0]
            number = record[1]
            pageFirst = record[2]
            pageLast = record[3]
            pub_year = record[4]
            title = record[5]
            author = record[6]

            try:
                c = models.AINZindex.objects.get(
                    volume=volume,
                    number=number,
                    pageFirst=pageFirst,
                    pageLast=pageLast,
                    pub_year=pub_year,
                    title=title,
                    author=author,
                )
                print "found an existing record"
                c.volume = volume
                c.number = number
                c.pageFirst = pageFirst
                c.pageLast = pageLast
                c.pub_year = pub_year
                c.title = title
                c.author = author

            except:
                c = models.AINZindex(
                    volume=volume,
                    number=number,
                    pageFirst=pageFirst,
                    pageLast=pageLast,
                    pub_year=pub_year,
                    title=title,
                    author=author,
                 )
            c.save()

        return 0

    def insert_reports(self, records):

        for record in records:
            report_id = record[0]
            author = record[1]
            title = record[2]
            date = record[3]
            region = record[4]
            authority_id = record[5]
            nzaa_id = record[6]

            try:
                c = models.HertNZ_digitalLibCat.objects.get(
                    report_id=report_id,
                    author=author,
                    title=title,
                    date=date,
                    region=region,
                    authority_id=authority_id,
                    nzaa_id=nzaa_id,
                )
                c.report_id = report_id
                c.author = author
                c.title = title
                c.date = date
                c.region = region
                c.authority_id = authority_id
                c.nzaa_id = nzaa_id
            except:
                c = models.HertNZ_digitalLibCat(
                    report_id=report_id,
                    author=author,
                    title=title,
                    date=date,
                    region=region,
                    authority_id=authority_id,
                    nzaa_id=nzaa_id,
                )

            c.save()

        return 0
