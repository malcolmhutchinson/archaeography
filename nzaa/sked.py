"""The download scheduler (sked).

Generates lists of NZAA site record identifiers, given an NZMS 260
sheet identifier and a maximum number.

Will be called from command line.
"""

import datetime


def sked(sheet, ordinal, fname=None):
    now = datetime.datetime.now()
    timestamp = str(now.replace(microsecond=0))
    output = "# The download scheduler at " + timestamp + "\n"
    output += "# Sheet: " + sheet + " Ordinal: " + str(ordinal) + "\n"
    output += "#\n"

    for n in range(1, ordinal + 1):
        output += sheet + '/' + str(n) + ' '
        if n % 10 == 0:
            output += '\n'

    output += "\n# END\n"

    if fname:
        f = open(fname, 'w')
        f.write(output)
    return output
