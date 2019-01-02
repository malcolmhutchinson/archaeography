"""Authorisation tests for the members application.


"""

import os
import settings
from home.authority import *
import models

def commands(request):

    if not request.user.is_authenticated:
        return None

    

    


