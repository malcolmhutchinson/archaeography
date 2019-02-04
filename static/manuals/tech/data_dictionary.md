Data dictionary
===============

This document describes the data structures involved in the project.
We model two datasets; the NZ Archaeological Association's Site
Recording Scheme, and geographic reference sets supplied by Land
Information NZ and Statistics NZ.

Database tables are held in the `public` schema of database
`archaeography` on a PostgreSQL/PostGIS installation.



The geolibrary
--------------

The geographic library, repository of data supplied by LINZ and
Statistics NZ, including topographic features (lakes, railways, roads,
rivers, cadastral parcels etc).

### Tables in the geolib section


    geolib_aerialfile

        Index to files associated with an aerial photo frame. No
        geometry (geometry from aerialframe).

    geolib_aerialframe

        Index to aerial photo frames, with georeferencing
        information. Polygon geometries.

    geolib_aerialrun

        Index to runs of aerial frames. Polygon geometry sum of the
        frames.  

    geolib_aerialsurvey

        Index to historic aerial photo surveys. Polygon geometry sum
        of the runs.

    geolib_cadastre

        Copy of the LINZ cadastral dataset. Polygon geometries.

    geolib_lidarset

        Index to selected lidar sets sourced from LINZ. Polygon
        geometries.

    geolib_lidartile

        Tile index for the lidar collection Polygon geometries.

    geolib_nzmsgrid

        An idealised grid describing NZMS260 sheet locations. Derived
        mathematically, this is not the sheet index. Polygon geometries
        
    geolib_orthoset

        Index to selected orthophoto sets sourced from LINZ. Polygon
        geometries.

    geolib_orthotile

        Tile index for the orthophoto collection Polygon geometries.

    geolib_placename

        Copy of the LINZ placename dataset, point geometries.

    geolib_region

        Copy of Statistics NZ region boundaries. Polygon geometries.
        
    geolib_territorialauthority

        Copy of Statistics NZ territorial authority boundaries.
        Polygon geometries.

    geolib_topo50_island

        Copy of the LINZ dataset. Polygon geometries.

    geolib_topo50_lake

        Copy of the LINZ dataset. Polygon geometries.

    geolib_topo50_rail

        Copy of the LINZ dataset. Linestring geometries.

    geolib_topo50_riverline

        Copy of the LINZ dataset. Linestring geometries.

    geolib_topo50_riverpoly

        Copy of the LINZ dataset. Polygon geometries.

    geolib_topo50_road

        Copy of the LINZ dataset. Linestring geometries.

    geolib_topo50grid

        An idealised grid describing Topo50 sheet locations. Derived
        mathematically, this is not the sheet index. Polygon geometries.
        
    geolib_topocontour20metre

        Copy of the LINZ dataset. Linestring geometries.

    geolib_topomapseries

        Index to the topographic map collections. No geometry.

    geolib_topomap

        Index to individual topographic map sheets. Polygon geometry.

    geolib_topomapfile

        Index to files associated with a topomap sheet. Tracks
        versions of the sheet.

    geolib_waterways

        Selected coastline and waterways, combined from Topo50 data
        and tracings from topographic maps.




<br />

The nzaa application
--------------------

The model of the Site Recording Scheme, this is the core of the
archaeography project.


### Tables in the nzaa app

    nzaa_actor

        A named person or organisation found in the site records.

    nzaa_actor_sites

        Link table.
        
    nzaa_feature

        Unique feature descriptors extracted from the site record
        collection.

    nzaa_feature_sites

        Link table.
        
    nzaa_newsite

        Site records for previously-unrecorded archaeological
        sites. Kept separate from the official site record
        collection. 

    nzaa_periods

        Unique period descriptors extracted from the site record
        collection.

    nzaa_periods_sites

        Link table.
        
    nzaa_site

        Archaeological site records. 

    nzaa_sitelist

        User-compiled lists of site records.

    nzaa_sitelist_sites

        Link table.
        
    nzaa_sitereview

        Table containing change records for site records.

    nzaa_sitetypes

        Unique values for 'site type' extracted from the site
        records.
        
    nzaa_sitetypes_sites

        Link table.
        
    nzaa_update

        Site update records, associsted with a site record.



