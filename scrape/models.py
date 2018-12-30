# -*- coding: utf-8 -*-
"""Models (database tables) for library sources
"""

from __future__ import unicode_literals
from django.db import models
import biblio.models


class AINZcontents(models.Model):
    """Archaeology in NZ contents Vol31-53.

    Index by author of the articles in Archaeology in NZ.

        Fields: Author, Year, Title, Citation

    The issue code is (eg) "31(3): 142-152" which breaks down to

        [Vol]([No]): [pageFirst]-[pageLast]

    """

    author = models.TextField(blank=True, null=True)
    year = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    citation = models.TextField(blank=True, null=True)

    provenance = models.TextField(blank=True, null=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name='Record created at')

    def _clean_citation(self):
        return self.citation.replace('–', '-')

    cite = property(_clean_citation)

    def _authors_list(self):
        """Provide a list of authors associated with each record.

        These are extracted from the author column using the following
        structure:

            (surname), (firstname), (sec_author) [and (sec_author)]

        """
        authors = []
        first_author = None
        middle_authors = []
        last_author = None

        first_cut = self.author.split('and')

        if len(first_cut) == 1:
            names = first_cut[0].split(',')
            if len(names) == 2:
                first_author = (names[0].strip(), names[1].strip())
            else:
                first_author = (first_cut[0], '')

        elif len(first_cut) == 2:
            last = first_cut[1].strip()
            names = last.split(' ')
            last_author = (names[1].strip(), names[0].strip())

            names = first_cut[0].split(',')
            first_author = (names[0].strip(), names[1].strip())

            middle = names[2:]
            for author in middle:
                names = author.strip().split(' ')
                middle_authors.append((names[1].strip(), names[0].strip()))

        authors.append(first_author)
        authors.extend(middle_authors)
        if last_author:
            authors.append(last_author)

        return authors

    authors_list = property(_authors_list)

    def compute_issue_data(self):
        """The hyphen character is u2013 """
        volume = ''
        number = ''
        pageFirst = ''
        pageLast = ''

        return (volume, number, pageFirst, pageLast)


class AINZindex(models.Model):
    """Archaeology in NZ contents.

    Archaeology in NZ. Title and author by volume and number, starting
    a Vol 1 No 1, ending with Vol 58 No 1.

        Fields: Volume, Number, PageFirst, PageLast, Title, Author

    """

    volume = models.TextField(blank=True, null=True)
    number = models.TextField(blank=True, null=True)
    pageFirst = models.TextField(blank=True, null=True)
    pageLast = models.TextField(blank=True, null=True)
    pub_year = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)

    provenance = models.TextField(blank=True, null=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name='Record created at')

    def _authors_list(self):
        """Provide a list of author tuples with last and first names.

        Example values:

            Adkin, G.L.
            Groube, L.M. and R. Green
            Golson, Jack and R.N. Brothers
            Maddock, K.J. and A. Taylor
            Knox, F.B., K.R. Cairns and M. Hitchings
            Wilkes, Owen, Ron Scarlett and George Boraman
            M.M.T. (Michael Trotter)
            P.G. (Peter Gathercole)

        Split by "and" giving

        """
        authors = []
        first_author = None
        middle_authors = []
        last_author = None

        first_cut = self.author.split(' and')

        if len(first_cut) == 1:
            names = first_cut[0].split(',')
            if len(names) == 2:
                first_author = (names[0].strip(), names[1].strip())
            else:
                first_author = (first_cut[0], '')

        elif len(first_cut) == 2:
            last = first_cut[1].strip()
            names = last.split(' ')
            last_author = (names[1].strip(), names[0].strip())

            names = first_cut[0].split(',')
            first_author = (names[0].strip(), names[1].strip())

            middle = names[2:]
            for author in middle:
                names = author.strip().split(' ')
                middle_authors.append((names[1].strip(), names[0].strip()))

        authors.append(first_author)
        authors.extend(middle_authors)
        if last_author:
            authors.append(last_author)

        return authors

    authors_list = property(_authors_list)

    def _compute_citation(self):
        """ """

        citation = self.volume + "(" + self.number + "): "
        citation += self.pageFirst + unicode("-") + self.pageLast
        return citation

    cite = property(_compute_citation)

    def _get_issue(self):
        cut1 = self.cite.split(':')
        return cut1[0]

    g = property(_get_issue)


class AINZlinks(models.Model):
    """ """

    volume = models.IntegerField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    year = models.CharField(max_length=16, blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)

    def _get_paper(self):

        ps = biblio.models.Paper.objects.filter(
            issue__publication__identifier='AINZ',
            title=self.title,
            issue__volume=self.volume,
            issue__number=self.number
        )
        if len(ps) == 1:
            return ps[0]
        elif len(ps) > 1:
            print "Multiple papers found for ", self.id
            print "Vol", self.volume, "No", self.number, self.title

        else:
            print "No paper found for record", self.id
            print "Vol", self.volume, "no", self.number, self.title

    paper = property(_get_paper)


class HertNZ(models.Model):
    """Heritage NZ digital library catalogue.

    Index by author of reports to HNZ.

        Fields: Report_identifier, Author, Title, Date,
                TrustRegion, AuthorityNo, SiteNo

    """

    report_id = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)
    region = models.TextField(blank=True, null=True)
    authority_id = models.TextField(blank=True, null=True)
    nzaa_id = models.TextField(blank=True, null=True)

    provenance = models.TextField(blank=True, null=True)
    created = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name='Record created at')

    def _get_issue(self):
        """Return an biblio.Issue object which this report belongs to."""

        i = None
        pub_date = None
        pubid = 'NZHPT'
        year = ''
        try:
            int(self.date)
            pub_date = self.date + '-01-01'
        except ValueError:
            i = biblio.models.Issue.objects.get(id=556)

        if pub_date:
            i = biblio.models.Issue.objects.get(
                publication__identifier=pubid,
                pub_date=pub_date,
            )

        if i:
            return i
        else:
            return None

    issue = property(_get_issue)

    def _get_pub_date(self):
        """Return a string formatted as a data from the date field."""

        try:
            int(self.date)
            pub_date = self.date + '-01-01'
        except ValueError:
            pub_date = '1900-01-01'

        return pub_date

    pub_date = property(_get_pub_date)

    def _authors_list(self):
        """Return a list of authors from the author column.

        Authors are identified as:

            (last_name), (first name)[ | (last_name), (first_name)]

        Example values:

            Allen, Melinda S.|Wallace, Rod| Bader, Hans-Dieter|Parker, Daniel
            Allingham, Brian J.
            Bedford, Stuart H.|Clark, Deresley|Sutton, Doug

        Return (last_name, first_name) tuples.

        """

        authors = []
        first_author = None
        middle_authors = []
        last_author = None

        author = self.author

        first_pass = author.split(u'\u2502')
        if len(first_pass) == 1:
            first_pass = self.author.split('|')

        if len(first_pass) == 1:
            names = first_pass[0].split(',')
            if len(names) == 2:
                authors.append((names[0].strip(), names[1].strip()))
            else:
                authors.append((names[0].strip(), ''))

        else:
            for item in first_pass:
                names = item.split(',')
                if len(names) == 2:
                    authors.append((names[0].strip(), names[1].strip()))
                else:
                    authors.append((names[0].strip(), ''))

        return authors

    authors_list = property(_authors_list)

    def list_sites():
        sites = []
        return sites

    def _get_archaeologists(self):
        archaeologists = []
        a = self.authors_list
        for author in a:
            try:
                a = biblio.models.Archaeologist.objects.get(
                    name_first__contains=author[1],
                    name_last__contains=author[0])
                archaeologists.append(a)
            except biblio.models.Archaeologist.DoesNotExist:
                try:
                    a = biblio.models.Archaeologist.objects.get(
                        initials__contains=author[1],
                        name_last__contains=author[0])
                    archaeologists.append(a)
                except biblio.models.Archaeologist.DoesNotExist:
                    print "No match on ", self.id,
                    print "author[0]", author[0], "author[1]", author[1]

                except biblio.models.Archaeologist.MultipleObjectsReturned:
                    print "Multiple matches on ", self.id, self.author

            except biblio.models.Archaeologist.MultipleObjectsReturned:
                print "Multiple matches on first name for ", self.id,
                print "author", author[0], author[1]
        return archaeologists

    archaeologists = property(_get_archaeologists)


class NZJAcontents(models.Model):
    """To hold data scraped from NZAA website index of NZJA.
    """

    volume = models.IntegerField()
    year = models.IntegerField()
    first_author = models.CharField(max_length=255)
    authors = models.CharField(max_length=255, blank=True, null=True)
    title = models.TextField()
    link = models.TextField()

    def _get_pub_date(self):
        return str(self.year) + '-01-01'

    pub_date = property(_get_pub_date)

    def __unicode__(self):
        return str(self.volume) + " " + str(self.year)

    def _get_archaeologists(self):
        """Return a list of archaeologist objects repreesenting the authors.

        These arrive in the first_author and authors fields. The first
        contains single names, with first name initial and last name.

            Fiona Petchey
            Patrick D. Nunn
            Marianne Turner
            Kevin L. Jones

        The authors field contains zero or more names separated by semicolons:

            Jaques Bolé; André Ouetcho
            Foss Leach; Mike Burtenshaw; Graham Harris

        """

        archaeologists = []
        not_recognised = []
        names = self.first_author.split(' ')
        first_name = names[0].strip()
        last_name = names[-1].strip()

        a = biblio.models.Archaeologist.objects.filter(
            name_last=last_name)

        if len(a) > 1:
            a = a.filter(
                name_last__contains=last_name,
                name_first__contains=first_name)

        if len(a) == 0:
            a = biblio.models.Archaeologist.objects.filter(
                initials__contains=first_name,
                name_last__contains=last_name)

        if len(a) == 1:
            archaeologists.append(a[0])
        elif len(a) == 0:
            not_recognised.append((self.first_author, first_name, last_name))
        elif len(a) > 1:
            print "Multiple authors found in first author: ", self.id

        authors = self.authors.split('; ')

        for author in authors:
            if len(author) > 0:
                names = author.split(' ')
                first_name = names[0].strip()
                last_name = names[-1].strip()

                a = biblio.models.Archaeologist.objects.filter(
                    name_first__contains=first_name,
                    name_last__contains=last_name)

                if len(a) == 0:
                    a = biblio.models.Archaeologist.objects.filter(
                        initials__contains=first_name,
                        name_last__contains=last_name)

                if len(a) == 1:
                    archaeologists.append(a[0])
                elif len(a) == 0:
                    not_recognised.append((author, first_name, last_name))
                elif len(a) > 1:
                    print "Multiple authors found: ", len(a), len(author)

        return archaeologists

    archaeologists = property(_get_archaeologists)


class JPAcontents(models.Model):
    """To hold data scraped from NZAA website for the index of teh JPA.
    """

    volume = models.IntegerField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    authors = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
