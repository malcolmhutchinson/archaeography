"""Authorisation tests for the NZAA application.

Two kinds of functions in this module: ones which return True or
False, and those which supply lists of commands.

True-orFalse functions are used to settle questions like 'are you
allowed to edit this update record' or 'are you a member of the nzaa
group?'

These methods work by knocking out contenders; if you are not
authenticated, return False. If you pass that, next question.

"""
import os
import settings
from home.authority import *
import models


def boundaries(request):
    """Is the user a member of the boundaries group?"""

    if not request.user.is_authenticated:
        return False

    if not request.user.groups.filter(name='boundary'):
        return False

    return True

def boundary_commands(request):
    """Return a list of (link, text) tuples listing authorised commands."""
    
    if not request.user.is_authenticated:
        return None

    boundary_url = os.path.join(
        settings.BASE_URL, 'boundaries/')

    upload_url = os.path.join(
        settings.BASE_URL, 'boundary/upload/')

    
    commands = [
        (boundary_url, 'your boundary reports'),
        (upload_url, 'upload a boundary file'),
    ]

    return commands


def commands(request, site=None, update=None, sitelist=None, newsite=None):

    if not request.user.is_authenticated:
        return None

    commands = [
        (settings.BASE_URL + 'newsites/', 'new site records'),
        (settings.BASE_URL + 'changes/', 'recent changes'),
        (settings.BASE_URL + 'sitelists/', 'site lists'),
    ]

    if 'sitelist' in request.path:
        commands.append((
            settings.BASE_URL + 'sitelists/' + request.user.username,
            'your site lists')
        )
        commands.append(
            (settings.BASE_URL + 'sitelist/create', 'new site list')
        )

    if models.Update.objects.filter(owner=request.user.username).count():
        commands.append((settings.BASE_URL + 'updates/' + request.user.username,
            'your update records'))
        
    if site:

        archsite = settings.SITE_PAGE + site.nzaa_id
        commands.append((archsite, 'visit archsite page'))

        if update_this_site(request.user, site):
            commands.append(
                (os.path.join(site.url, 'update'), 'update this site record')
            )
        commands.append(
            (os.path.join(site.url, 'review'), 'review this site record'))

    if update:
        if (edit_this_update(request.user, update) and
                'edit' not in request.path):
            commands.append(
                (os.path.join(update.url, 'edit'), 'edit this update record')
            )

    if sitelist:
        commands.append(
            (sitelist.url, sitelist.name),
        )

    if (not request.path == settings.BASE_URL + 'create/' and
            'sitelist' not in request.path):
        commands.append((settings.BASE_URL + 'create/',
                         'create a site record'))

    if newsite:
        if newsite.owner == request.user.username:
            commands.append(
                (os.path.join(newsite.url, 'edit'), 'edit this record')
            )

    return commands


def edit_this_update(user, update):
    """Can this user edit this update?

    The filekeeper can edit any update with ordinal above 0.

    A user can edit this update if they own it and the status is not
    submitted.

    """

    if not user.is_authenticated:
        return False

    if user.groups.filter(name='filekeeper'):
        return True

    if user.username == update.owner and update.status != 'Submitted':
        return True

    return False


def filekeeper(user):
    """Is the user a member of the group filekeeper?"""

    if not user.is_authenticated:
        return False

    if user.groups.filter(name='filekeeper'):
        return True

    return False


def filekeeper_commands(request, site=None):
    """Produce a list of (link, text) tuples, commands for a filekeeper."""

    path = request.path

    commands = [
    ]

    if site:
        commands.append(
            (os.path.join(settings.BASE_URL, site.nzaa_id, 'scrape/'),
             'scrape this record'),
        )

    elif len(path) > 0:
        path = path.replace('/nzaa/', '')
        path = path.replace('scrape/', '')
        path = path.replace('assess/', '')
        if len(path) > 0 and path[-1] == '/':
            path = path[0:-1]
        if '/' in path:
            (sheet, ordinal) = path.split('/')
            if sheet in settings.NZMS260:
                commands.append(
                    (os.path.join(settings.BASE_URL, path, 'scrape/'),
                     'scrape this record'),
                )

    commands.append(
        (os.path.join(settings.BASE_URL, 'filekeeper/submitted/'),
            'submitted updates')
    )
    return commands


def nzaa_member(user):
    """Can the user see an NZAA archaeological site record?

    Must be a member of the nzaa group.
    """
    if not user.is_authenticated():
        return False

    if not user.groups.filter(name='nzaa'):
        return False

    return True


def update_this_site(user, site):
    """Can this user update this site?

    If they are a member of group nzaa, and they do not have an update
    record pending or submitted.

    """
    if not user.is_authenticated():
        return False

    if not user.groups.filter(name='nzaa'):
        return False

    try:
        updates = models.Update.objects.get(
            site_id=site.nzaa_id, owner=user.username)
        return False
    except models.Update.DoesNotExist:
        return True

    return True
