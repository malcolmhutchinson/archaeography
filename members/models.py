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

import os
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from markdown2 import markdown

import settings
import webnote


class Member(models.Model):
    """A member has a login on the system, linked to a User object.

    This table stores additional information about the person who is
    the member.

    """

    URL = 'member'

    number = models.AutoField(primary_key=True)
    user = models.OneToOneField(User)
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

    def filespace(self):
        """Return a webnote directory object of this user's webspace."""

        docroot = settings.STATICFILES_DIRS[0].replace('static', '')

        return webnote.Directory(self.filespace_path(), docroot=docroot)
    
    def filespace_path(self):
        """Return a string to the filespace for this user."""

        return os.path.join(
            settings.STATICFILES_DIRS[0],
            self.URL,
            self.user.username,
        )

    def mkdir(self):
        """Create a directory in the member filespace."""
        
        if not os.path.isdir(self.filespace_path()):
            os.mkdir(self.filespace_path())

        return None
     
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


