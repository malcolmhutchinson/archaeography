"""Settings file for geolibrary application.
"""

import os
from home.settings import *

BASE_URL = '/geolib/'
BASE_FILESPACE = os.path.join(STATICFILES_DIRS[0], 'geolib/')

# Used to identify aerial photograph frames.
VALID_RUN_IDS = (
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
)
