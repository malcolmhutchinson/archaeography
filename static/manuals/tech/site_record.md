The site record
===============

The unit of the SRS is the indivdual archaeological site record.

A site record describes the archaeological features of a place. It
comprises a location expressed as map coordinates, short category
fields, and written descriptions of the place, the archaeological
evidence and the condition of the site. It may include photographs,
maps or other matter describing or illustrating the archaeological
evidence.

A site record is created when an archaeologist records archaeological
evidence found at a place where such evidence has not previously been
recorded.

A site record may be updated an arbitrary number of times after it has
been created, by archaeologists recording observations from subsequent
visits, or adding more photos, maps or historic material.


### Composition

The site record contains

-   _aggregate_ fields storing short values, like `site type`,
    `ethnicity`, `period`  and so on, which are commonly used as search
    terms. 

-   _long_ fields with text content of arbitrary length, including
    descriptions of the place, the archaeological evidence and
    condition of the place.

-   _files_ associated with the record, like photographs, scanned pages,
    PDF documents and other electronic files.

-   _administrative_ fields logging change activity and recording the
    identities of people making changes to the record.

The first three constitute the archaeological data in a site
record. The files are particularly important, as a large number of
older records are expressed in the collection as scans of original
paper documents. In many cases, these image files contain the only
archaeological data in the record, as aggregate and long fields have
not been captured for them.


### Architecture

A site record in our model is expressed as an object in the
`nzaa_site` table, which links to one or many records in the
`nzaa_update` table.

All site records have at least one update record; that being update
zero; the copy of the ArchSite record. This may comprise several
update events; descrete instances of when new matter has been
introduced into the site file. These instances are discernable from
the files in the record, and can be modelled in the archaeography
project. 

The process of 'normalising' a site record involves identifying each
of these descrete update events, and creating an update record for
them.

A normalised site record would have one `Update` object for the intial
recording event, and one for each update event after that. The files
representing the paper document will be associated with each update
record.

We will be able to count all the documents in the collection, and
make calculated estimates of the average volume of data per site. We
will be able to identify patterns in the change history; locations in
which records are often being updated, or areas in which many of the
archaeological records have not been recently updated.

In the Django web framework, Python language classes called _models_
describe the structure of database tables, and provide methods to to
perform calculations on the data in the tables.


### Fields

Many fields are shared between the `Site`, `NewSite` and `Update`
tables. These shared fields are:

    ordinal              Integer part of NZAA id.
    site_name


    These are mostly copies of the ArchSite fields, but they can be
    changed in this dataset.

    site_type
    site_subtype         A guess at a subtyping system.
    location
    period
    ethnicity
    landuse
    threats
    features
    associated_sites
    visited
    visited_by


    Geographic data
    
    easting              Integer of NZTM coord
    northing             Integer
    radius               Estimation of curtilige
    geom                 Point geometry
    geom_poly            Polygoy derived from data about the site


    Administration fields

    created
    created_by
    modified
    mdified_by
    accessioned
    accessioned_by
    provenance
    extracted
    log
    owner
    edit
    allow
    deny



Fields unique to `Site`

    Identifiers and locations.

    nzaa_id
    nzms_id
    nzms_sheet
    tla
    region
    island


    Site assessment fields

    record_quality       Estimation of quality.
    assessed
    assessed_by


    These fields are direct copies of the record in ArchSite.

    lgcy_assocsites
    lgcy_capmethod
    lgcy_condition
    lgcy_ethnicity
    lgcy_evidence
    lgcy_inspected
    lgcy_landuse
    lgcy_period
    lgcy_shortdesc
    lgcy_status
    lgcy_features
    lgcy_threats
    lgcy_type
    lgcy_easting
    lgcy_northing


    Administration fields

    recorded             Date
    recorded_by          Name
    update               Date
    updated_by           Name
    status
    digest               MD5 hash of the record contents. Used in
                         change detection
    last_change          Date




### Methods

Methods shared with `NewSite` and `Update`.

    airphoto
    archsite_url
    clean_log
    closest_placenames
    closest_road
    closest_sites
    display_assoc_sites
    display_condition
    display_created
    display_description
    display_finder_aid
    display_introduction
    display_modified
    display_references
    display_rights
    display_site_type
    display_visited
    distance_to_coast
    _nzmg_coords
    distance_to_coast_str
    distance_to_water
    footprint
    get_aerial_frames
    get_easting
    get_island
    get_northing
    get_nzms_sheet
    get_point_parcel
    get_parcels
    get_region
    get_tla
    get_topo50_sheet
    legacy_coords
    latitude
    lidar_tiles
    link_site_ids
    list_actors
    list_features
    list_periods
    long_fields_text
    longitude
    mapfile
    mapsheets
    nzmg_coords
    nzmg_gridref
    nztm_coords
    ortho_tiles
    parcels
    primary_coast
    primary_waterway
    replace_temp_ids
    update_actors
    unref_figs
    wrap_field
    wgs_coords


    


