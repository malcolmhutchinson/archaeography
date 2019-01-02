#! /bin/bash
## setup.sh

## archaeograhy project setup script.

# This script injects shapefile data from LINZ and Stats NZ into a
# PostgreSQL database cluster named 'archaeography'. The schema
# `work.` is created to keep the injected records in, until an SQL file
# is run to copy them into the working tables in the schema `public.`

# Last updated 2019-01-03 as the boundary report version.


# Pick up the legacy data from sql file.
#psql -d arch_breport < ~/dev/arch/code/setup/migratedata.sql

# Create the work schema.
echo 'CREATE SCHEMA IF NOT EXISTS work' | psql -d arch_breport

### Inject the NZMS1 series from an sql file.
psql -d arch_breport < ~/dev/arch/code/setup/nzms1.sql

#### Inject the shapefiles into the database work. schema.

# NZ Coastlines and islands
shp2pgsql -d -s 2193 -g geom nz-coastlines-and-islands-polygons-topo-150k \
          work.islands | psql -d arch_breport

# 20 m contours
shp2pgsql -d -s 2193 -g geom nz-contours-topo-150k-1 work.contours \
    | psql -d arch_breport
shp2pgsql -a -s 2193 -g geom nz-contours-topo-150k-2 work.contours \
    | psql -d arch_breport
shp2pgsql -a -s 2193 -g geom nz-contours-topo-150k-3 work.contours \
    | psql -d arch_breport

# Topo 50 Lakes polygon
shp2pgsql -d -s 2193 -g geom nz-lake-polygons-topo-150k work.lakes \
    | psql -d arch_breport

# NZMS 260
shp2pgsql -d -s 2193 -g geom  nzms-260-map-sheets work."nzms260" \
    | psql -d arch_breport

# NZ Place Names (WGS84)
shp2pgsql -d -s 4326 -g geom nz-place-names-nzgb work.placenames \
    | psql -d arch_breport

# NZ Railway centrelines
shp2pgsql -d -s 2193 -g geom nz-railway-centrelines-topo-150k work.rail \
    | psql -d arch_breport

# NZ river centrelines
shp2pgsql -d -s 2193 -g geom nz-river-centrelines-topo-150k work.river_line \
    | psql -d arch_breport

# NZ river polygons
shp2pgsql -d -s 2193 -g geom nz-river-polygons-topo-150k work.river_poly \
    | psql -d arch_breport

# NZ road subsections
shp2pgsql -d -s 2193 -g geom nz-road-centrelines-topo-150k work.roads \
    | psql -d arch_breport

# Topo 50
shp2pgsql -d -s 2193 -g geom nz-topo-50-map-sheets work."topo50" \
    | psql -d arch_breport

# Regional councils
shp2pgsql -d -s 2193 -g geom regional-council-2013 work.region \
    | psql -d arch_breport

# Territorial authorities
shp2pgsql -d -s 2193 -g geom TA2017_HD_Clipped work.ta \
    | psql -d arch_breport

# Various aerial imagery index tiles
shp2pgsql -d -s 2193 -g geom auckland-05m-rural-aerial-photos-index-tiles-2010-2012 work.aerial_auckland \
    | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom canterbury-075m-rural-aerial-photos-index-tiles-2004-2010 work.aerial_canterbury \
    | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom dunedin-04m-rural-aerial-photos-index-tiles-2013 work.aerial_dunedin \
    | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom gisborne-04m-rural-aerial-photos-index-tiles-2012-2013 work.aerial_gisborne \
    | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom otago-075m-rural-aerial-photos-index-tiles-2004-2011 work.aerial_otago \
    | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom waikato-05m-rural-aerial-photos-index-tiles-2012-2013 work.aerial_waikato \
    | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom wellington-lidar-index-tiles-2013 work.aerial_wellington \
    | psql -d arch_breport

# Various Lidar index tiles
shp2pgsql -d -s 2193 -g geom \
          auckland-lidar-index-tiles-2013 \
          work.lidar_auckland | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom \
          bay-of-plenty-tauranga-and-coast-lidar-index-tiles-2015 \
          work.lidar_bop | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom \
          canterbury-christchurch-and-selwyn-lidar-index-tiles-2015 \
          work.lidar_canterbury | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom \
          waikato-west-coast-and-hauraki-plains-lidar-index-tiles-2015 \
          work.lidar_waikatocoast | psql -d arch_breport

shp2pgsql -d -s 2193 -g geom wellington-lidar-index-tiles-2013 \
          work.lidar_wellington | psql -d arch_breport

# NZ Property parcels
shp2pgsql -d -s 2193 -g geom nz-parcels-1 work.cadastre \
    | psql -d arch_breport
shp2pgsql -a -s 2193 -g geom nz-parcels-2 work.cadastre \
    | psql -d arch_breport
shp2pgsql -a -s 2193 -g geom nz-parcels-3 work.cadastre \
    | psql -d arch_breport
shp2pgsql -a -s 2193 -g geom nz-parcels-4 work.cadastre \
    | psql -d arch_breport
shp2pgsql -a -s 2193 -g geom nz-parcels-5 work.cadastre \
    | psql -d arch_breport

### Now start running SQL to move these things into position.
echo 'Running populate_geolib.sql'
psql -d arch_breport < ~/dev/arch/code/setup/populate_geolib.sql






