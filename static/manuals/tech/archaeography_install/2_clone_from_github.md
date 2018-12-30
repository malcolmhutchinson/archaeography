Clone the archaeography code from GitHub
========================================


Download a copy of the code repository from GitHub. In shell:

Before this: 

This software is dependant on another Python project,
[webnote](https://github.com/malcolmhutchinson/webnote). You must
clone the code for this into your local filesystem, and make it
available to the archaeography code. In shell:

    # Create a working space for archaeography and for the webnote app.
    mkdir ~/dev
    mkdir ~/dev/archaeography ~/dev/webnote  

    # Clone from archaeography from GitHub.
    git clone https://github.com/malcolmhutchinson/archaeography.git \
        ~/dev/archaeography/code

    # Clone webnote from GitHub.
    git clone https://github.com/malcolmhutchinson/webnote.git \
        ~/dev/webnote

    # Virtual environment for archaeography.
    cd ~/dev/archaeography
    virtualenv env

    # Install Python packages
    pip install \
        Pillow bs4 django ephem exifread markdown2 \
        mechanize psycopg2-binary requests smartypants

    # Place a symlink to the webnote code.
    ln -s ~/dev/webnote/code/webnote ~/dev/webnote/env/lib/python2.7/site-packages/webnote


You will need to enter your password for the machine role, into a
variable in `~/dev/archaeography/code/home/settings.py`. Copy this
value, or write it down: (the bit inside the quotes, where it says
'some pass phrase'. Obviously, you will want to change this in your
installation).

MACHINE = ('django_superuser_id', 'some pass phrase')


Next: [Install PostgreSQL](psql_install)



