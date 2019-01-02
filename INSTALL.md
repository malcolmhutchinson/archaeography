Installing the archaeography project
====================================

This document explains how to download and install the archaeography
code into a Django development project. It does not provide
instruction for deploying the archaeography project into a production
environment.


Introduction
------------

The archaeography project is an experimental model of the NZ
Archaeological Association's Site Recording Scheme. It is an
engineering prototype, the purpose of which is to provide
understanding of the problems involved with handling large volumes of
information describing archaeological sites.

This experiment is expressed in the Python programming language, using
the Django web framework. 

The project depends on geographic reference data, and there are
scripts which will help download these from sources on the public
internet; specifically, Topo50 (and other) datasets from
[Land Information New Zealand](http://linz.govt.nz) and the region and
territorial authority boundaries from [Statistics
NZ](https://www.stats.govt.nz/).

There are no archaeological data in this codebase. To do anything
interesting with the project, you will have to download copies of the
site records from [ArchSite](http://www.archsite.org.nz/), and in
order to do this you will need a username and password from the NZ
Archaeological Association.

It helps a lot if you are already familiar with setting up Django
projects, and installing PostgreSQL. It is beyond the scope of this
document to step through that stuff, but there is plenty of helpful
information out there.

This document assumes installation on a Linux machine, although I see
no reason why it won't work on other OSs.



Setting up
----------

The steps to be taken are:

1.  Install and configure the PostgreSQL server

2.  Clone the code from GitHub

3.  Install the project database tables

4.  Add users and groups

5.  Download reference geographic data from LINZ and Stats NZ.

6.  Populate the geographic data library with reference sets. 

7.  Download reference raster datasets into the geolibrary.

8.  Download copies of archaeological records from ArchSite.

9.  (Optional) copy proprietary data from a legacy system.



Step 1: Install and configure the PostgreSQL server
---------------------------------------------------

This script assumes a Debian GNU/Linux host.

In shell:

    # Update the repository lists.
    sudo apt-get update

    # Install PostgreSQL and PostGIS
    sudo apt-get install postgresql postgresql-contrib postgis

    # Become the user `postgres`.
    sudo su postgres

    # Create users. The P flag prompts for passwords.
    createuser -P machine

    # Create the database, with owner `machine`.
    createdb -O machine archaeography

    # create the PostGIS extension.
    psql -d archaeography -c "CREATE EXTENSION postgis;"

You will need to create a user account for yourself, and give it the
privileges of the `machine` account. Create the user in shell, then go
to the DBMS to grant privileges.

    createuser -P malcolm
    psql -d archaeography -c "GRANT machine TO malcolm;"



Step 2.  Clone the code from GitHub
-----------------------------------

This software is dependant on another Python project,
[webnote](https://github.com/malcolmhutchinson/webnote). You must
clone the code for this into your local filesystem, and make it
available to the archaeography code. In shell:

    # Create a working space for archaeography and for the webnote app.
    mkdir ~/dev
    mkdir ~/dev/arch ~/dev/webnote  

    # Clone archaeography from GitHub.
    git clone https://github.com/malcolmhutchinson/archaeography.git \
        ~/dev/arch/code

    # Clone webnote from GitHub.
    git clone https://github.com/malcolmhutchinson/webnote.git \
        ~/dev/webnote

    # Virtual environment for archaeography.
    cd ~/dev/arch
    virtualenv env
    source env/bin/activate

    # Install Python packages
    pip install \
        Pillow bs4 django ephem exifread markdown2 \
        mechanize psycopg2-binary requests smartypants

    # Place a symlink to the webnote code.
    ln -s ~/dev/webnote/ ~/dev/arch/env/lib/python2.7/site-packages/webnote


You will need to enter your password for the machine role, into a
variable in `~/dev/archaeography/code/home/settings.py`. Copy this
value, or write it down: (the bit inside the quotes, where it says
'some pass phrase'. Obviously, you will want to change this in your
installation).

    MACHINE = ('machine', 'some pass phrase')


Before you try to run any django management commands with
`runserver.py`, you will probably run into the missing secrets
file. You will see this error:

    ...
    File "~/dev/arch/code/home/settings.py", line 37, in <module>
      from secrets import *

This is looking for a file called `secrets.py` in the `home/`
directory. Look to the `settings.py` file in the same directory, and
comment this line:

    from secrets import *

Alternatively, follow the instructions in that settings file, and
create a secrets file. This is listed in .githubignore, so git will
ignore it. 


Step 3.  Install the project database tables
--------------------------------------------

Run the Django migrations to set up the database. In shell:

    cd ~/dev/arch/code
    source ../env/bin/activate

    # Run migrations to create the basic database structures.
    ./manage.py migrate

    # Make and run migrations for applications
    ./manage.py makemigrations geolib members nzaa
    ./manage.py migrate geolib
    ./manage.py migrate members
    ./manage.py migrate nzaa

    # Create static directories
    mkdir static/nzaa



Step 4.  Add users and groups
-----------------------------

Groups and users for the archaeography project

In shell:

    cd ~/dev/archaeography/code
    source ../env/bin/activate
    ./manage.py createsuperuser

Follow the prompts. Then start the development server, and point a
browser at `localhost:8000/admin`. Using the Django admin interface,
create the following group:

    nzaa

Using the django admin interface, create as many user records as
required, adding membership to the appropriate groups.

The archaeography project tracks information on membership, so that
we can control access to our copies of the archaeological records. Use
the Django admin panel to add a member record for your user.


Step 5: Downloading reference data
----------------------------------

The software in the archaeography project depends on certain
geographic files available from New Zealand government sources. All
these data are distributed under the Creative Commons licenses, and
can be downloaded free of charge.

You will be downloading ESRI shapefiles, packed into zip
archives. You should create a temporary directory, and unpack all the
zipfiles into it. 

-   Cadastre - NZ Primary parcels layer (LINZ)  
    [https://data.linz.govt.nz/layer/50772-nz-primary-parcels/](https://data.linz.govt.nz/layer/50772-nz-primary-parcels/)  
     NOTE. This is a very large file, and it changes weekly. It will
    likely come in a package with three or four separate shapefiles.

-   Index to NZMS260 (LINZ)  
    [https://data.linz.govt.nz/layer/51579-nzms-260-map-sheets/](https://data.linz.govt.nz/layer/51579-nzms-260-map-sheets/)

-   Index to Topo50 (LINZ)  
    [https://data.linz.govt.nz/layer/50295-nz-topo-50-map-sheets/](https://data.linz.govt.nz/layer/50295-nz-topo-50-map-sheets/)   

-   NZ Parcels  
    [https://data.linz.govt.nz/layer/51571-nz-parcels/data/](https://data.linz.govt.nz/layer/51571-nz-parcels/data/)  

    This is one of the larger geographic datasets we copy. At time of
    writing it came in at ~1.3 Gb. It is also updated weekly by LINZ.

-   NZ Place Names Gazetteer (LINZ)  
    [https://data.linz.govt.nz/layer/51681-nz-place-names-nzgb/](https://data.linz.govt.nz/layer/51681-nz-place-names-nzgb/)  
    CHECK the projection is EPSG:4326 (WGS84). You'll avoid a lot of
    heartache if you set this before downloading this layer.
    
-   NZ Railway centrelines (LINZ)  
    [https://data.linz.govt.nz/layer/50319-nz-railway-centrelines-topo-150k/](https://data.linz.govt.nz/layer/50319-nz-railway-centrelines-topo-150k/)  
    CHECK the projection is set to EPSG:2193 (NZTM2000).

-   Regional Councils 2013 (Stats NZ)  
    [https://datafinder.stats.govt.nz/layer/25738-regional-council-2013/](https://datafinder.stats.govt.nz/layer/25738-regional-council-2013/)

-   Territorial Authority 2017 (Stats NZ)  
    
    We require clipped TA boundaries, to avoid the "Area outside
    Territorial Authority" for sites which appear on the south western
    coastlines, whose coords may be off the side of the island.

    These are available to download along with a huge package, from
    Stats NZ at
    [http://archive.stats.govt.nz/browse_for_stats/Maps_and_geography/Geographic-areas/digital-boundary-files.aspx](http://archive.stats.govt.nz/browse_for_stats/Maps_and_geography/Geographic-areas/digital-boundary-files.aspx)

    The version I've selected is the top of the list of ESRI
    shapefiles, [New Zealand 2017 clipped high def (NZTM) (616MB)](http://www3.stats.govt.nz/digitalboundaries/annual/ESRI_Shapefile_2017_Digital_Boundaries_High_Def_Clipped.zip?_ga=2.16085878.1394924501.1525145876-573342339.1511210338)

    The one you want, inside that enormous pile of boundary
    shapefiles, is the one called `TA2017_HD_Clipped`

-   Topo50 twenty metre contours (LINZ)  
    [https://data.linz.govt.nz/layer/50768-nz-contours-topo-150k/](https://data.linz.govt.nz/layer/50768-nz-contours-topo-150k/)  
    NOTE: This is a large file (~1.7 Gb).
    
-   Topo50 Coastlines and Islands (LINZ)  
    [https://data.linz.govt.nz/layer/51153-nz-coastlines-and-islands-polygons-topo-150k/](https://data.linz.govt.nz/layer/51153-nz-coastlines-and-islands-polygons-topo-150k/)
    
-   Topo50 Lake polygons (LINZ)  
    [https://data.linz.govt.nz/layer/50293-nz-lake-polygons-topo-150k/](https://data.linz.govt.nz/layer/50293-nz-lake-polygons-topo-150k/)

-   Topo50 NZ River Centrelines (LINZ)  
    [https://data.linz.govt.nz/layer/50327-nz-river-centrelines-topo-150k/](https://data.linz.govt.nz/layer/50327-nz-river-centrelines-topo-150k/)

-   Topo50 road centrelines (LINZ)  
    [https://data.linz.govt.nz/layer/50329-nz-road-centrelines-topo-150k/data/](https://data.linz.govt.nz/layer/50329-nz-road-centrelines-topo-150k/data/)

-   Topo50 River polygons (LINZ)  
    [https://data.linz.govt.nz/layer/50328-nz-river-polygons-topo-150k/](https://data.linz.govt.nz/layer/50328-nz-river-polygons-topo-150k/)


Significant aerial image sets

-   Auckland 0.5m Rural Aerial Photos Index Tiles (2010-2012)  
    [https://data.linz.govt.nz/layer/51880-auckland-05m-rural-aerial-photos-index-tiles-2010-2012/](https://data.linz.govt.nz/layer/51880-auckland-05m-rural-aerial-photos-index-tiles-2010-2012/)

-   Canterbury 0.75m Rural Aerial Photos Index Tiles (2004-2010)  
    [https://data.linz.govt.nz/layer/51893-canterbury-075m-rural-aerial-photos-index-tiles-2004-2010/](https://data.linz.govt.nz/layer/51893-canterbury-075m-rural-aerial-photos-index-tiles-2004-2010/)

-   Dunedin 0.4m Rural Aerial Photos Index Tiles (2013)  
    [https://data.linz.govt.nz/layer/52112-dunedin-04m-rural-aerial-photos-index-tiles-2013/](https://data.linz.govt.nz/layer/52112-dunedin-04m-rural-aerial-photos-index-tiles-2013/)

-   Gisborne 0.4m Rural Aerial Photos Index Tiles (2012-2013)
    [https://data.linz.govt.nz/layer/51749-gisborne-04m-rural-aerial-photos-index-tiles-2012-2013/](https://data.linz.govt.nz/layer/51749-gisborne-04m-rural-aerial-photos-index-tiles-2012-2013/)

-   Otago 0.75m Rural Aerial Photos Index Tiles (2004 - 2011)  
    [https://data.linz.govt.nz/layer/51895-otago-075m-rural-aerial-photos-index-tiles-2004-2011/](https://data.linz.govt.nz/layer/51895-otago-075m-rural-aerial-photos-index-tiles-2004-2011/)

-   Waikato 0.5m Rural Aerial Photos Index Tiles (2012-2013)  
    [https://data.linz.govt.nz/layer/51883-waikato-05m-rural-aerial-photos-index-tiles-2012-2013/](https://data.linz.govt.nz/layer/51883-waikato-05m-rural-aerial-photos-index-tiles-2012-2013/)

-   Wellington 0.1m Urban Aerial Photos Index Tiles (2012-13)  
    [https://data.linz.govt.nz/layer/51912-wellington-01m-urban-aerial-photos-index-tiles-2012-13/](https://data.linz.govt.nz/layer/51912-wellington-01m-urban-aerial-photos-index-tiles-2012-13/)



Lidar indices to main centres

-   Auckland Lidar Index Tiles (2013)   
    [https://data.linz.govt.nz/layer/53407-auckland-lidar-index-tiles-2013/](https://data.linz.govt.nz/layer/53407-auckland-lidar-index-tiles-2013/)

-   Bay of Plenty - Tauranga and Coast LiDAR Index Tiles (2015)  
    [https://data.linz.govt.nz/layer/53575-bay-of-plenty-tauranga-and-coast-lidar-index-tiles-2015/](https://data.linz.govt.nz/layer/53575-bay-of-plenty-tauranga-and-coast-lidar-index-tiles-2015/)

-   Canterbury - Christchurch and Selwyn LiDAR Index Tiles (2015)     
    [https://data.linz.govt.nz/layer/53578-canterbury-christchurch-and-selwyn-lidar-index-tiles-2015/](https://data.linz.govt.nz/layer/53578-canterbury-christchurch-and-selwyn-lidar-index-tiles-2015/)

-   Waikato - West Coast and Hauraki Plains Lidar Index Tiles (2015)  
    [https://data.linz.govt.nz/layer/53624-waikato-west-coast-and-hauraki-plains-lidar-index-tiles-2015/](https://data.linz.govt.nz/layer/53624-waikato-west-coast-and-hauraki-plains-lidar-index-tiles-2015/)
    
-   Wellington Lidar Index tiles ()   
    [https://data.linz.govt.nz/layer/53591-wellington-lidar-index-tiles-2013/](https://data.linz.govt.nz/layer/53591-wellington-lidar-index-tiles-2013/)

Each one of these layers should be downloaded as shapefiles, with the
projection set to EPSG:2193, NZTM2000 (except for the place names
layer, which should be in EPSG:2143, WGS84).

Unpack all the shapefiles into a temporary directory. I did this at
`~/work/data/`, and I had 217 separate files, for these 30 shapefiles,
using up 12GB:

    auckland-05m-rural-aerial-photos-index-tiles-2010-2012
    auckland-lidar-index-tiles-2013
    bay-of-plenty-tauranga-and-coast-lidar-index-tiles-2015
    canterbury-075m-rural-aerial-photos-index-tiles-2004-2010
    canterbury-christchurch-and-selwyn-lidar-index-tiles-2015
    dunedin-04m-rural-aerial-photos-index-tiles-2013
    nz-coastlines-and-islands-polygons-topo-150k
    nz-contours-topo-150k-1
    nz-contours-topo-150k-2
    nz-contours-topo-150k-3
    nz-lake-polygons-topo-150k
    nzms-260-map-sheets
    nz-parcels-1
    nz-parcels-2
    nz-parcels-3
    nz-parcels-4
    nz-parcels-5
    nz-place-names-nzgb
    nz-railway-centrelines-topo-150k
    nz-river-centrelines-topo-150k
    nz-river-polygons-topo-150k
    nz-road-centrelines-topo-150k
    nz-topo-50-map-sheets
    otago-075m-rural-aerial-photos-index-tiles-2004-2011
    regional-council-2013
    TA2017_HD_Clipped
    waikato-05m-rural-aerial-photos-index-tiles-2012-2013
    waikato-west-coast-and-hauraki-plains-lidar-index-tiles-2015
    wellington-01m-urban-aerial-photos-index-tiles-2012-13
    wellington-lidar-index-tiles-2013

This is important because the scripts will choke if any of the
shapefiles are missing.  


Step 6: Populate the geographic data library
--------------------------------------------

Scripts to assist the install and setup process are kept in `setup/`,
and accessed from `setup/setup.sh`.

Check execute privileges are set on the file at
`~/dev/arch/code/setup/setup.sh`, and review it. 

It will copy the NZMS1 map series geometries from a file in setup, and
proceed to inject the geographic data from LINZ and Statistics NZ into
the database. This takes a bit of time.

CD to the directory where your shapefiles are stored, and run the
setup script:

    cd ~/work/data
    ~/dev/arch/code/setup/setup.sh

This takes a while. It creates a schema `work`, and copies all the
geographic reference data into it, from the shapefiles in the data
directory. It then executes a number of SQL statements to copy these
data into the appropriate project tables.

If desired, run this SQL code on the database, to remove the working
tables.

    DROP TABLE work.aerial_auckland;
    DROP TABLE work.aerial_canterbury;
    DROP TABLE work.aerial_dunedin;
    DROP TABLE work.aerial_gisborne;
    DROP TABLE work.aerial_otago;
    DROP TABLE work.aerial_waikato;
    DROP TABLE work.aerial_wellington;
    DROP TABLE work.cadastre1;
    DROP TABLE work.cadastre2;
    DROP TABLE work.cadastre3;
    DROP TABLE work.cadastre4;
    DROP TABLE work.cadastre5;
    DROP TABLE work.contours;
    DROP TABLE work.islands;
    DROP TABLE work.lakes;
    DROP TABLE work.lidar_auckland;
    DROP TABLE work.lidar_bop;
    DROP TABLE work.lidar_canterbury;
    DROP TABLE work.lidar_waikatocoast;
    DROP TABLE work.lidar_wellington;
    DROP TABLE work.nzms1;
    DROP TABLE work.nzms260;
    DROP TABLE work.placenames;
    DROP TABLE work.rail;
    DROP TABLE work.region;
    DROP TABLE work.river_line;
    DROP TABLE work.river_poly;
    DROP TABLE work.roads;
    DROP TABLE work.ta;
    DROP TABLE work.topo50;


### Python setup scripts

Now run the Python setup scripts, from the Django shell.

    cd ~/dev/arch/code
    source ../env/bin/activate
    ./manage.py shell

    # Create two derived map grid layers, for NZMS260 and Topo50.

    import geolib.utils as utils
    r = utils.GenerateNZMS260grid(commit=True)
    q = utils.GenerateTopo50grid(commit=True)


Step 7: Download reference raster datasets
------------------------------------------

The project also uses topographic map sets as reference
documents. These are scanned sheets rendered in GeoTiff image format
which contain data for projecting the map images into a GIS.

We use three topographic map series:

-   the current national topographic map series, Topo50  
    Land Information New Zealand  
    [http://topo.linz.govt.nz/Topo50_raster_images/TIFFTopo50/](http://topo.linz.govt.nz/Topo50_raster_images/TIFFTopo50/)
    
-   the older metric NZMS260 series  
    Auckland University public FTP server  
    [https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_260/geotif/](https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_260/geotif/)

-   the original imperial series NZMS1  
    Auckland University public FTP server  
    [https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_001/geotif/](https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_001/geotif/)

The steps we need to perform are:

1.  download the GeoTiff files,
1.  catalogue the files by associating them with a sheet record. 
1.  produce a script which generates PNG copies of them, for inline
    display in a browser,

There are hundreds of files in these collections. Downloading them all
takes a long time. There is code provided in the `geolib.utils` module
to do the job for you. Utilise this code from the Django Python shell:

    cd ~/dev/arch/code
    ../env/bin/activate
    ./manage.py shell

Then, in the Python shell:

    import geolib.utils as utils
    p = utils.TopoMaps()
    p.download()
    p.catalogue()
    
When I did this, it generated 2198 file records.     

The map images are held in a filesystem in the static files
hierarchy. These are kept in `static/geolib/map_[suffix]`, where
`[suffix]` is a lowercase representation of the map series code, thus:

    static/geolib/map_nzms1
    static/geolib/map_nzms260
    static/geolib/map_topo50

The `download` program will put them in there, and `catalogue` will
look for them there.



Step 8: Downloading archaeological records from ArchSite
--------------------------------------------------------

First, enter your Archiste username and password into
`home/settings/LOGIN_ARCHSITE`. This is a Python dictionary structure
containing `(username, password)` tuples. Replace the tuple keyed
`default` with your details.

Now the scrape utility can be used. It can be given a list of NZAA
identifiers, or the NZMS260 sheet identifier, and will create a set of
records locally populated with data from ArchSite.

Use the Django shell command:

    cd ~/dev/arch/code
    ../env/bin/activate
    ./manage.py shell

    import nzaa.scrape as scrape
    import nzaa.settings as settings
    targets = list(settings.NZMS260)
    s = scrape.Scrape(targets, verbose=True)
    
The series of commands listed above will set out to download the
entire collection from ArchSite. In my experience, this takes betwenn
10 and 12 hours.

It won't get the whole lot the first time. The program looks to
existing records for each NZMS260 sheet, finds the highest ordinal
number, and adds 50 to it. If you start with zero records, most sheets
will end up with 50. Run the scrape code a second time, and you'll get
to 100. And so on.



Step 9: Copying non-generic data
--------------------------------

This step is about migrating data generated by the project from a
running source host to a new installation. This includes the local
copy of the archaeological records, as well as the aerial photo
georeferencing information.

The process assumes a previouly-running installation, in which these
proprietary datasets are held. The first step is to make a copy of
these into the local host.

The relevant tables on the source must be copied into a work schema,
so they can be transferred to a similar schema on the host, where they
are staged for injection.

In shell on the source:

    # Run the SQL script to create the copy
    cd /opt/archaeography/code/setup/
    pdql -d archaeography < copy-into-work.sql

    # Dump the resulting schema into a file
    pg_dump -n work -O archaeography | gzip > ~/tmp/data.sql.gz

Copy the resulting file `data.sql.gzip` to the destination host,
unpack it and inject it into the work schema of the destination
database.

In shell, on the destination:

    # Uncompress the file and run it against the local db.
    gunzip data.sql.gz
    psql -d archaeography < data.sql

    # Run the script to copy the data into the live tables.
    ~/dev/archaeography/code/setup/copy-to-public.sql

References and links
--------------------

New Zealand Archaeological Association  
[https://nzarchaeology.org/](https://nzarchaeology.org/)

NZAA Site Recording Scheme ArchSite  
[http://www.archsite.org.nz/](http://www.archsite.org.nz/)





<div style='display: none;'>

</div>