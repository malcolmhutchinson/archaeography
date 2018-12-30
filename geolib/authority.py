"""Authority computer for the geolib application.

"""

import os
import settings
from home.authority import *
import models

COMMANDS = [
    (settings.BASE_URL + 'airphoto/', "aerial photos"),
    (settings.BASE_URL + 'cadastre/', "cadastral parcel search"),
    (settings.BASE_URL + 'lidar/', "lidar"),
    (settings.BASE_URL + 'ortho/', "orthophotos"),
    (settings.BASE_URL + 'topo/', "topographic maps"),
]


def commands(request):
    """Build the command set."""

    commands = COMMANDS

    return commands


def librarian(user):
    """Is the user a member of the group librarians?"""

    if not user.is_authenticated:
        return False

    if user.groups.filter(name='librarian'):
        return True

    return False


def librarian_commands(request):
    if not request.user.groups.filter(name='librarian'):
        return None

    path = request.path

    commands = [
        (os.path.join(settings.BASE_URL, 'airphoto/newframe/'),
            'new frame record'),
    ]
    return commands
