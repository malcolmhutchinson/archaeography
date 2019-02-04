"""Authorisation code for the members application.

"""

import os
import settings

from django.contrib.auth.models import User
from nzaa.authority import *


def nzaa_member(user):
    """Is the user a member of the nzaa group?"""
    
    if not user.is_authenticated:
        return False

    if not nzaa.authority.nzaa_member(user):
        return False

    return True
