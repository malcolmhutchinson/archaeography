"""Short bits of code to do useful things.

"""

import nzaa.settings as settings


def is_siteid(thing):
    """Validate a string to be a possible NZAA id

    E.g. "T14/22". The part before the slash must be a valid NZMS 260
    sheet identifier, and the part after must resolve to an integer.

    """
    p = 0

    try:
        sheet, ordinal = thing.split('/')
    except:
        return False

    try:
        p = int(ordinal)
    except:
        return False

    if (not p):        # Trap 0.
        return False

    if sheet not in settings.NZMS260:
        return False

    return True


def thousands_dep(x):
    """Turn an integer into a string with comma separators.

    This works with extended slice syntax; [begin:end:step]. By
    leaving begin and end off, and stepping -1, it reverses the
    string.

    """
    if type(x) not in [type(0), type(0L)]:
        raise TypeError("Parameter must be an integer.")

    sx = str(x)[::-1]

    c = 1
    o = ''
    for s in sx:
        if c == 4:
            o += ','
            c = 1

        o += s
        c += 1

    return o[::-1]
