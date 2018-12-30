Fields in a site record
=======================

Throughout this manual, I refer to the _aggregate fields_ in a site
record. These are the fields containing short terms like site type and
ethnicity, which are most commonly used to search on.

    site type
    site subtype
    location
    period
    ethnicity
    landuse
    threats


Aggregate fields are distinct from the _long fields_ which may contain
text data of arbitrary length, and are not commonly used in search
terms. 

    introduction
    finder_aid
    description
    condition
    references
    rights

There are fields to store the names of people who recorded and updated
the site record.

    recorded
    recorded_by
    updated
    updated_by
    visited
    visited_by
    
In addition, a site record contains a list of _legacy fields_. These
are duplications of the aggregate fields intended to record the values
in the ArchSite record. These are kept separately, and cannot be
modified by users.

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

There are also fields derived from geographic computations, which
associate site records with places, like the regions or territorial
authorities. These are computed once, and then stored, to enable quick
returns on common geographic queries.

    nzms_sheet
    region
    tla
    island

Finally, each site record also contains _administration fields_ which
are used to track when the record was created and modified, whether it
has been assessed for quality, or when a new record or update was
accessioned into the official collection, and to keep a log of changes
to that site record.

    accessioned
    accessioned_by
    assessed
    assessed_by
    created
    created_by
    modified
    modified_by
    provenance
    extracted
    log
    
    