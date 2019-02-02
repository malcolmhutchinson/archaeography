"""Authorisation code for the members application.

"""

import os
import settings

from django.contrib.auth.models import User

import nzaa.authority


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
        settings.BASE_URL, request.user.username, 'boundaries/')

    upload_url = os.path.join(
        settings.BASE_URL, 'upload/boundary/')

    
    commands = [
        (boundary_url, 'your boundary files'),
        (upload_url, 'upload a boundary file'),
    ]

    return commands


def nzaa_member(user):
    """Is the user a member of the nzaa group?"""
    
    if not user.is_authenticated:
        return False

    if not nzaa.authority.nzaa_member(user):
        return False

    return True
