-- populate_geolib.sql
--
-- Archaeography project geodata library collection.

-- This script copies records from schema work, into the library
-- tables.

-- Last updated 2018-05-04.




-- Topo 50 island.

-- This is needed by code to generate map grid layers. It needs to
-- know where the land is, and it uses this table to do so.
-- 1
INSERT INTO "geolib_topo50_island" (
    "id",
    "identifier",
    "name",
    "group",
    "provenance",
    "geom"
)
SELECT
    nextval('geolib_topo50_island_id_seq'),
    "name",
    "name",
    "grp_name",
    'LINZ data injected ' || clock_timestamp(),
    "geom"
FROM work.islands
;

-- Regional councils. Depended on by placenames.
-- 2
INSERT INTO "geolib_region" (
    "id",
    "identifier",
    "name",
    "provenance",
    "geom"
)
SELECT
    nextval('geolib_region_id_seq'),
    replace(lower(regc2013_1), ' ', ''),
    regc2013_1,
    'NZ Stats data injected ' || clock_timestamp(),
    geom
FROM work.region
;



-- 20 m contours
-- 3
INSERT INTO "geolib_topocontour20metre" (
    "id",
    "elevation",
    "provenance",
    "geom"
)
SELECT
    nextval('geolib_topocontour20metre_id_seq'),
    elevation,
    'LINZ data injected ' || clock_timestamp(),
    ST_Force2D(geom)
FROM work.contours
;

-- Topo 50 lakes polygon
-- 4
INSERT INTO "geolib_topo50_lake" (
    "id",
    "name",
    "provenance",
    "geom"
)
SELECT
    nextval('geolib_topo50_lake_id_seq'),
    name,
    'LINZ data injected ' || clock_timestamp(),
    geom
FROM work.lakes
;

-- Railway centrelines
-- 5
INSERT INTO geolib_topo50_rail (
    "id",
    name,
    track_type,
    provenance,
    geom
)
SELECT
    nextval('geolib_topo50_rail_id_seq'),
    name,
    track_type,
    'LINZ data injected ' || clock_timestamp(),
    geom
FROM work.rail
;

-- LINZ river data do not contain names for the rivers. 
-- River centrelines
-- 6
INSERT INTO geolib_topo50_riverline(
    "id",
    "stream_order",
    "provenance",
    "geom"
)
SELECT
    nextval('geolib_topo50_riverline_id_seq'),
    1,
    'LINZ data injected ' || clock_timestamp(),
    geom
FROM work.river_line
;

-- River polygons
-- 7
INSERT INTO geolib_topo50_riverpoly(
    id,
    provenance,
    geom
)
SELECT
    nextval('geolib_topo50_riverpoly_id_seq'),
    'LINZ data injected ' || clock_timestamp(),
    geom
FROM work.river_poly
;

-- NZ road subsections
-- 8
INSERT INTO geolib_topo50_road (
    id,
    name,
    hway_num,
    way_count,
    status,
    surface,
    provenance,
    geom
)
SELECT
    nextval('geolib_topo50_road_id_seq'),
    name,
    hway_num,
    way_count,
    status,
    surface,
    'LINZ data injected ' || clock_timestamp(),
    geom
FROM work.roads
;

-- NZ Place names. Depends on geolib_region being populated.

-- The file from LINZ is unprojected Lat/Long, and contains many
-- places which are well outside the areas covered by the NZAA
-- archaeological dataset. We want to select only those placenames
-- which are inside NZ regions.
--   This is a costly computation. Find the union of all the regions,
-- convert it to WGS84, and compare each placename in work.placenames
-- for intersection with this.
--   We also transform the resulting point values to NZTM 2000 as we
-- inject them into the destination table.
-- 9
INSERT INTO geolib_placename (
    id,
    name,
    status,
    feat_type,
    land_district,
    info_ref,
    info_origin,
    info_description,
    provenance,
    geom
)
SELECT
    nextval('geolib_placename_id_seq'),
    name,
    status,
    feat_type,
    land_distr,
    info_ref,
    info_origi,
    info_descr,
    'LINZ data injected' || clock_timestamp(),
    ST_Transform(geom, 2193)
FROM work.placenames
WHERE
    ST_Intersects (
        geom,
        ST_Transform((SELECT ST_Union(geom) FROM geolib_region), 4326)
    )
;

-- Territorial authorities
-- 10
INSERT INTO geolib_territorialauthority (
    id,
    identifier,
    name,
    provenance,
    geom
)
SELECT
    nextval('geolib_territorialauthority_id_seq'),
    replace(lower(ta2017_nam), ' ', ''),
    ta2017_nam,
    'Stats NZ data inserted ' || clock_timestamp(),
    geom
FROM work.ta
;

--  Topographic map index, comprising data from LINZ, and the Auckalnd
--  University.


-- Set up the map series.
-- 11
INSERT INTO geolib_topomapseries (
    series, description, source_instution, uri
)
VALUES
(
    'NZMS1',
    'Imperial measure, inch to mile series.',
    'University of Auckland, Cartographic and Geospatial Resources Repository.',
    'https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_001/geotif/'
),
(
    'NZMS260',
    'Metric series now superseded. 1:50K scale.',
    'University of Auckland, Cartographic and Geospatial Resources Repository.',
    'https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_2601/geotif/'
),
(
    'TOPO50',
    'Metric maps in current use. 1:50k scale.',
    'Land Information New Zealand (LINZ)',
    'http://topo.linz.govt.nz/Topo50_raster_images/GeoTIFFTopo50/'
)
;

-- NZMS1 series from work.nzms1
INSERT INTO geolib_topomap (
    id,
    name,
    sheet_id,
    series_id,
    projection,
    provenance,
    geom
)
SELECT
    nextval('geolib_topomap_id_seq'),
    name, sheet_id,
    'NZMS1',
    'SIYG',
    'https://gdh.auckland.ac.nz/maps/LINZ/NZMS/NZMS_001/geotif/ downloaded 2018-05-21',
    geom
FROM work.nzms1
;

-- Insert the two extra sheet records NZMS260 P26, R25, in work.nzms260
-- 12
INSERT INTO work.nzms260 (
    sheet, name, geom
)
VALUES
(
    'R25',
    'Te Horo',
    ST_GeomFromText('MULTIPOLYGON((
       (1779982 5508287,
        1779982 5478285,
        1760001 5478318,
        1759832 5508206,
        1779982 5508287)
    ))', 2193)
),
(
    'P26',
    'French Pass',
    ST_GeomFromText('MULTIPOLYGON((
       (1659994 5478282,
        1699986 5478284,
        1699986 5448289,
        1659994 5448290,
        1659994 5478282)
    ))', 2193)

);
-- Copy NZMS 260 index into the map index.
-- 13
INSERT INTO geolib_topomap (
    id,
    name,
    sheet_id,
    series_id,
    projection,
    provenance,
    geom
)
SELECT
    nextval('geolib_topomap_id_seq'),
    name,
    sheet,
    'NZMS260',
    'NZGD1949',
    'LINZ data inserted ' || clock_timestamp(),
    geom
FROM work.nzms260
;

-- Copy Topo 50 index into the map index.
-- 14
INSERT INTO geolib_topomap (
    id,
    name,
    sheet_id,
    series_id,
    projection,
    provenance,
    geom
)
SELECT
    nextval('geolib_topomap_id_seq'),
    sheet_name,
    sheet_code,
    'TOPO50',
    'NZMS2000',
    'LINZ data inserted ' || clock_timestamp(),
    geom
FROM work.topo50
;


-- Aerial imagery tiles.
-- Set up the imagery sets.
-- 15
INSERT INTO geolib_orthoset (
    identifier, name, year_captured, imagelayer_uri
)
VALUES
(
    'AKLD050-2012',
    'Auckland 0.5m Rural Aerial Photos (2010-2012)',
    2012,
    'https://data.linz.govt.nz/layer/1769'
),
(
    'CANT075-2010',
    'Canterbury 0.75m Rural Aerial Photos (2004-2010)',
    2010,
    'https://data.linz.govt.nz/layer/1933'
),
(
    'DUN040-2013',
    'Dunedin 0.4m Rural Aerial Photos (2013)',
    2013,
    'https://data.linz.govt.nz/layer/2109'
),
(
    'GISB040-2013',
    'Gisborne 0.4m Rural Aerial Photos (2012-2013)',
    2013,
    'https://data.linz.govt.nz/layer/1722'
),
(
    'OTG075-2011',
    'Otago 0.75m Rural Aerial Photos (2004 - 2011)',
    2011,
    'https://data.linz.govt.nz/layer/1910'
),
(
    'WAI050-2013',
    'Waikato 0.5m Rural Aerial Photos (2012-2013)',
    2013,
    'https://data.linz.govt.nz/layer/1872'
),
(
    'WGTN010-2013',
    'Wellington 0.1m Urban Aerial Photos (2012-13)',
    2013,
    'https://data.linz.govt.nz/layer/1871'
);
-- Copy the individual records from schema work.
-- Auckland aerials.
-- 16
INSERT INTO geolib_orthotile (
    id,
    series_id, identifier, provenance, geom
    )
SELECT
    nextval('geolib_orthotile_id_seq'),
    'AKLD050-2012', sheet_no, 'LINZ, flown ' || date_flown, geom
FROM work.aerial_auckland;

-- Canterbury
-- 17
INSERT INTO geolib_orthotile (
    id,
    series_id, identifier, provenance, geom
    )
SELECT
    nextval('geolib_orthotile_id_seq'),
    'CANT075-2010', tile_nam, 'LINZ, flown ' || date_flown, geom
FROM work.aerial_canterbury;

-- Dunedin
-- 18
INSERT INTO geolib_orthotile (
    id,
    series_id, identifier, provenance, geom
    )
SELECT
    nextval('geolib_orthotile_id_seq'),
    'DUN040-2013', substring(name, 10, 9), 'LINZ, flown ' || flown, geom
FROM work.aerial_dunedin;

-- Gisborne
-- 19
INSERT INTO geolib_orthotile (
    id,
    series_id, identifier, provenance, geom
    )
SELECT
    nextval('geolib_orthotile_id_seq'),
    'GISB040-2013', tile_name, 'LINZ, flown ' || acq_date, geom
FROM work.aerial_gisborne;

-- Otago
-- 20
INSERT INTO geolib_orthotile (
    id,
    series_id, identifier, provenance, geom
    )
SELECT
    nextval('geolib_orthotile_id_seq'),
    'OTG075-2011', datastor_n, 'LINZ, flown ' || fly_date, geom
FROM work.aerial_otago;

-- Waikato
-- 21
INSERT INTO geolib_orthotile (
    id,
    series_id, identifier, provenance, geom
    )
SELECT
    nextval('geolib_orthotile_id_seq'),
     'WAI050-2013', tile_name, 'LINZ, flown ' || flying_dat, geom
FROM work.aerial_waikato;

-- Wellington
-- 22
INSERT INTO geolib_orthotile (
    id,
    series_id, identifier, provenance, geom
    )
SELECT
    nextval('geolib_orthotile_id_seq'),
    'WGTN010-2013', substring(tile, 5, 19), 'LINZ', geom
FROM work.aerial_wellington;


-- Lidar tiles.
-- Set up the lidar sets.
-- 23
INSERT INTO geolib_lidarset (
    name, identifier, year_captured, imagelayer_uri
)
VALUES
(
    'Auckland Lidar (2013)',
    'AUK2015',
    2013,
    'https://data.linz.govt.nz/layer/3405'
),
(
    'Bay of Plenty - Tauranga and Coast LiDAR (2015)',
    'BOP2015',
    2015,
    'https://data.linz.govt.nz/layer/3556'
),
(
    'Canterbury - Christchurch and Selwyn LiDAR (2015)',
    'CANT2015',
    2015,
    'https://data.linz.govt.nz/layer/3587'
),
(
    'Waikato - West Coast and Hauraki Plains LiDAR (2015)',
    'WAICOAST2015',
    2015,
    'https://data.linz.govt.nz/layer/3622'
),
(
    'Wellington LiDAR (2013)',
    'WELL2013',
    2013,
    'https://data.linz.govt.nz/layer/3621'
);
--- Auckland Lidar.    
-- 23
INSERT INTO geolib_lidartile (
    id,
    identifier, series_id, provenance, geom
)
SELECT
    nextval('geolib_lidartile_id_seq'),
    sheet_no, 'AUK2015', 'LINZ, flown ' || date_flown, geom
FROM work.lidar_auckland;

-- Bay of Plenty Lidar.
-- 24
INSERT INTO geolib_lidartile (
    id,
    identifier, series_id, provenance, geom
)
SELECT
    nextval('geolib_lidartile_id_seq'),
    name, 'BOP2015', 'LINZ', geom
FROM work.lidar_bop;

-- Canterbury Lidar.
-- 25
INSERT INTO geolib_lidartile (
    id,
    identifier, series_id, provenance, geom
)
SELECT
    nextval('geolib_lidartile_id_seq'),
    tilename, 'CANT2015', 'LINZ', geom
FROM work.lidar_canterbury;

-- Waikato Lidar.
-- 26
INSERT INTO geolib_lidartile (
    id,
    identifier, series_id, provenance, geom
)
SELECT
    nextval('geolib_lidartile_id_seq'),
    name, 'WAICOAST2015', 'LINZ', geom
FROM work.lidar_waikatocoast;

-- Wellington Lidar.
-- 27
INSERT INTO geolib_lidartile (
    id,
    identifier, series_id, provenance, geom
)
SELECT  
    nextval('geolib_lidartile_id_seq'),
    substring(tile, 5, 19), 'WELL2013', 'LINZ', geom
FROM work.lidar_wellington;

-- NZ property parcels into geolib_cadastre.
DELETE FROM work.cadastre WHERE geom is NULL;
INSERT INTO geolib_cadastre (
    id,
    appellation, affected_surveys, parcel_intent, topology_type,
    statutory_actions, land_district, titles, survey_area, calc_area,
    provenance, geom
)
SELECT
    nextval('geolib_cadastre_id_seq'),
    appellatio, affected_s, parcel_int, topology_t,
    statutory_, land_distr, titles, survey_are, calc_area,
    'LINZ 2018-06-08', geom
FROM work.cadastre;

