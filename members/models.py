"""Archaeography members models.

A member is someone who has a login identity on the site.

We would keep very basic contact information about
members. Ordinarily, an email address alone would be sufficient.

Each member should be able to alter their own member's record.


---

This can be extensively redrawn. I think the contacts table should
hold email addresses and phone numbers, with links to people and
organisations. This way, we can record as many phone numbers and emil
addresses against an organisation or person as we like.

"""

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

from nzaa.models import Site, Update, SiteList


class Address(models.Model):
    """Phone number, email address or other address. To be atached to a
    person or organisation record.
    """

    CATEGORY = (
        ('blog_personal', 'personal blog'),
        ('blog_work', 'professional blog'),
        ('email', 'email'),
        ('email_private', 'private email'),
        ('email_work', 'work email'),
        ('fax', 'fax'),
        ('phone_home', 'home phone'),
        ('phone_mob', 'mobile phone'),
        ('phone_office', 'office phone'),
        ('postal', 'postal address'),
        ('street', 'street address'),
        ('website', 'website'),
    )

    category = models.CharField(
        max_length=255, choices=CATEGORY, blank=True, null=True,)
    data = models.TextField()

    def __unicode__(self):
        return unicode(
            self.category + ": " + self.data[:20]
        )


class Contact(models.Model):

    """Organisations and people share certain fields and functions.
    """

    address = models.ManyToManyField(Address, blank=True)

    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    provenance = models.TextField(blank=True, null=True, editable=False)

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

    class Meta:
        abstract = True


class Organisation(Contact):
    """Contact details and biographical info about organisations."""

    name_short = models.CharField(max_length=255, blank=True, null=True)
    name_long = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name_short

    class Meta:
        ordering = ('name_short',)

    def __unicode__(self):
        return self.name_short

    def get_absolute_url(self):
        return ''

    url = property(get_absolute_url)


class Person(Contact):
    """Contact details and biographical info about people."""

    name_first = models.CharField(max_length=255, blank=True, null=True)
    name_last = models.CharField(max_length=255, blank=True, null=True)
    initials = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    citation = models.CharField(max_length=255, blank=True, null=True)
    organisation = models.ManyToManyField(Organisation, blank=True)

    def __unicode__(self):
        return self.name_last.upper() + ', ' + self.name_first


class Member(models.Model):
    """A member has a login on the system.
    """

    number = models.AutoField(primary_key=True)
    user = models.OneToOneField(User)
    person = models.OneToOneField(
        Person, on_delete=models.SET_NULL,
        blank=True, null=True
    )
    name = models.CharField(max_length=255)
    initial = models.CharField(
        max_length=16, blank=True, null=True, unique=True)
    nickname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    affiliation = models.CharField(max_length=255, blank=True, null=True)
    interests = models.TextField(blank=True, null=True)

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

    def __unicode__(self):
        if self.nickname:
            return unicode(self.nickname)
        return unicode(self.user.username)

    def lists(self):
        """Return a dictionary containing indications of site updates or lists.
        """
        sitelists = SiteList.objects.filter(owner=self.user.username).count()
        updates = Update.objects.filter(owner=self.user.username).count()

        interests = {
            'sitelists': sitelists,
            'updates': updates,
        }
        return interests

    def list_sitelists(self):
        """List the sitelists the user owns. """

        return SiteList.objects.filter(owner=self.user.username)

    def list_updates(self):
        """List the update records belonging to the user. """
