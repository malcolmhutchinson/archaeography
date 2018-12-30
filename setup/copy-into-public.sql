-- copy-into-public.sql

-- INSERT data from the work. schema into the project tables.  In
-- particular, insert the aerial photo georeferencing data, and the
-- NZAA records.

INSERT INTO geolib_aerialsurvey  (
    identifier,
    ordinal,
    name,
    year_first,
    film_type,
    rights,
    comments,
    geom,
    year_last
)

SELECT
    id,
    ordinal,
    name,
    year_first,
    film_type,
    rights,
    comments,
    geom,
    year_last

FROM work.geolib_aerialsurvey;

INSERT INTO geolib_aerialrun (
    id,
    identifier,
    ordinal,
    direction,
    rights,
    comments,
    geom,
    survey_id
)
SELECT
    id,
    identifier,
    ordinal,
    direction,
    rights,
    comments,
    geom,
    survey_id
FROM work.geolib_aerialrun;
SELECT setval('geolib_aerialrun_id_seq',
    (SELECT id FROM geolib_aerialrun ORDER BY id DESC LIMIT 1) + 1);


INSERT INTO geolib_aerialframe (
    id,
    identifier,
    ordinal,
    date_flown,
    time_flown,
    alt_ft,
    alt_m,
    focal_length,
    aperture,
    status,
    name,
    description,
    georef_notes,
    source_url,
    coverage,
    provenance,
    rights,
    geom,
    run_id
)
SELECT
    id,
    identifier,
    ordinal,
    date_flown,
    time_flown,
    alt_ft,
    alt_m,
    focal_length,
    aperture,
    status,
    name,
    description,
    georef_notes,
    source_url,
    coverage,
    provenance,
    rights,
    geom,
    run_id

FROM work.geolib_aerialframe;
SELECT setval('geolib_aerialframe_id_seq',
    (SELECT id FROM geolib_aerialframe ORDER BY id DESC LIMIT 1) + 1
);


--
--  NZAA archaeological site data
--
INSERT INTO nzaa_site (
    ordinal,
    site_name,
    other_name,
    site_type,
    site_subtype,
    location,
    period,
    ethnicity,
    landuse,
    threats,
    features,
    associated_sites,
    visited,
    visited_by,
    easting,
    northing,
    radius,
    geom,
    geom_poly,
    created,
    created_by,
    modified,
    modified_by,
    accessioned,
    accessioned_by,
    provenance,
    extracted,
    log,
    owner,
    edit,
    allow,
    deny,
    nzaa_id,
    nzms_id,
    nzms_sheet,
    island,
    tla,
    region,
    record_quality,
    assessed,
    assessed_by,
    lgcy_assocsites,
    lgcy_capmethod,
    lgcy_condition,
    lgcy_ethnicity,
    lgcy_evidence,
    lgcy_inspected,
    lgcy_landuse,
    lgcy_period,
    lgcy_shortdesc,
    lgcy_status,
    lgcy_threats,
    lgcy_type,
    lgcy_easting,
    lgcy_northing,
    recorded,
    recorded_by,
    updated,
    updated_by,
    status,
    lgcy_features,
    last_change,
    digest
    
)
SELECT
    ordinal,
    site_name,
    other_name,
    site_type,
    site_subtype,
    location,
    period,
    ethnicity,
    landuse,
    threats,
    features,
    associated_sites,
    visited,
    visited_by,
    easting,
    northing,
    radius,
    geom,
    geom_poly,
    created,
    created_by,
    modified,
    modified_by,
    accessioned,
    accessioned_by,
    provenance,
    extracted,
    log,
    owner,
    edit,
    allow,
    deny,
    nzaa_id,
    nzms_id,
    nzms_sheet,
    island,
    tla,
    region,
    record_quality,
    assessed,
    assessed_by,
    lgcy_assocsites,
    lgcy_capmethod,
    lgcy_condition,
    lgcy_ethnicity,
    lgcy_evidence,
    lgcy_inspected,
    lgcy_landuse,
    lgcy_period,
    lgcy_shortdesc,
    lgcy_status,
    lgcy_threats,
    lgcy_type,
    lgcy_easting,
    lgcy_northing,
    recorded,
    recorded_by,
    updated,
    updated_by,
    status,
    features,
    last_change,
    digest

FROM work.nzaa_site;

CREATE VIEW nzaa_site_view as
SELECT nzaa_id, site_name, site_type, site_subtype,
       easting, northing, nzms_sheet, ordinal,
       location, period, ethnicity, features, associated_sites,
       region, tla,
       lgcy_type, lgcy_period, lgcy_shortdesc, lgcy_condition,
       lgcy_ethnicity, lgcy_evidence, lgcy_inspected, lgcy_landuse,
       lgcy_threats, lgcy_easting, lgcy_northing,
       recorded, recorded_by, updated, updated_by, visited, visited_by,
       extracted,
       geom, geom_poly
FROM nzaa_site;

-- NZAA update data.

INSERT INTO nzaa_update (
    ordinal,
    site_id,
    site_name,
    other_name,
    site_type,
    site_subtype,
    location,
    period,
    ethnicity,
    landuse,
    threats,
    associated_sites,
    visited,
    visited_by,
    easting,
    northing,
    radius,
    geom,
    geom_poly,
    created,
    created_by,
    modified, modified_by,
    provenance,
    extracted,
    log,
    owner,
    edit,
    allow,
    deny,
    update_id,
    update_type,
    introduction,
    finder_aid,
    description,
    condition,
    "references",
    rights,
    update_note,
    nzmg_gridref,
    updated,
    updated_by,
    submitted,
    submitted_by,
    uploaded,
    uploaded_by,
    status,
    opstatus,
    new_id
)
SELECT
    ordinal,
    site_id,
    site_name,
    other_name,
    site_type,
    site_subtype,
    location,
    period,
    ethnicity,
    landuse,
    threats,
    associated_sites,
    visited,
    visited_by,
    easting,
    northing,
    radius,
    geom,
    geom_poly,
    created,
    created_by,
    modified, modified_by,
    provenance,
    extracted,
    log,
    owner,
    edit,
    allow,
    deny,
    update_id,
    update_type,
    introduction,
    finder_aid,
    description,
    condition,
    "references",
    rights,
    update_note,
    nzmg_gridref,
    updated,
    updated_by,
    submitted,
    submitted_by,
    uploaded,
    uploaded_by,
    status,
    opstatus,
    new_id
FROM work.nzaa_update;

INSERT INTO nzaa_actor (
    id,
    sourcename,
    fullname
)
SELECT
    id,
    sourcename,
    fullname
FROM work.nzaa_actor;
SELECT setval('nzaa_actor_id_seq',
    (SELECT id FROM nzaa_actor ORDER BY id DESC LIMIT 1) + 1);

INSERT INTO nzaa_actor_sites (
    id,
    actor_id,
    site_id
)
SELECT
    id,
    actor_id,
    site_id
FROM work.nzaa_actor_sites;
SELECT setval('nzaa_actor_sites_id_seq',
    (SELECT id FROM nzaa_actor_sites ORDER BY id DESC LIMIT 1) + 1);

INSERT INTO nzaa_feature (
    id,
    name
)
SELECT
    id,
    name
FROM work.nzaa_feature;
SELECT setval('nzaa_feature_id_seq',
    (SELECT id FROM nzaa_feature ORDER BY id DESC LIMIT 1) + 1);

INSERT INTO nzaa_feature_sites (
    id,
    feature_id,
    site_id
)
SELECT
    id,
    feature_id,
    site_id
FROM work.nzaa_feature_sites;
SELECT setval('nzaa_feature_sites_id_seq',
    (SELECT id FROM nzaa_feature_sites ORDER BY id DESC LIMIT 1) + 1);

INSERT INTO nzaa_periods (
    id,
    name
)
SELECT
    id,
    name
FROM work.nzaa_periods;
SELECT setval('nzaa_periods_id_seq',
    (SELECT id FROM nzaa_periods ORDER BY id DESC LIMIT 1) + 1);

INSERT INTO nzaa_periods_sites (
    id,
    periods_id,
    site_id
)
SELECT
    id,
    periods_id,
    site_id
FROM work.nzaa_periods_sites;
SELECT setval('nzaa_periods_sites_id_seq',
    (SELECT id FROM nzaa_periods_sites ORDER BY id DESC LIMIT 1) + 1);



-- NZAA site lists.

INSERT INTO nzaa_sitelist (
    id,
    name,
    long_name,
    subject,
    description,
    notes,
    list_type,
    owner,
    edit,
    allow,
    deny,
    created,
    created_by,
    modified,
    modified_by
)
SELECT
   id,
    name,
    long_name,
   subject,
    description,
    notes,
    list_type,
    owner,
    edit,
    allow,
    deny,
    created,
    created_by,
    modified,
    modified_by
FROM work.nzaa_sitelist;
SELECT setval('nzaa_sitelist_id_seq',
    (SELECT id FROM nzaa_sitelist ORDER BY id DESC LIMIT 1) + 1);

INSERT INTO nzaa_sitelist_sites (
    id,
    sitelist_id,
    site_id
)
SELECT
    id,
    sitelist_id,
    site_id
FROM work.nzaa_sitelist_sites;
SELECT setval('nzaa_sitelist_sites_id_seq',
    (SELECT id FROM nzaa_sitelist_sites ORDER BY id DESC LIMIT 1) + 1);



-- Site review record.

INSERT INTO nzaa_sitereview(
    id,
    reviewed,
    log,
    status,
    note,
    site_type,
    site_subtype,
    location,
    period,
    ethnicity,
    features,
    radius,
    associated_sites,
    recorded,
    recorded_by,
    updated,
    updated_by,
    visited,
    visited_by,
    record_quality,
    from_site_type,
    from_site_subtype,
    from_location,
    from_period,
    from_ethnicity,
    from_features,
    from_radius,
    from_associated_sites,
    from_recorded,
    from_recorded_by,
    from_updated,
    from_updated_by,
    from_visited,
    from_visited_by,
    from_record_quality,
    assessed_by,
    site_id
)
SELECT
    id,
    reviewed,
    log,
    status,
    note,
    site_type,
    site_subtype,
    location,
    period,
    ethnicity,
    features,
    radius,
    associated_sites,
    recorded,
    recorded_by,
    updated,
    updated_by,
    visited,
    visited_by,
    record_quality,
    from_site_type,
    from_site_subtype,
    from_location,
    from_period,
    from_ethnicity,
    from_features,
    from_radius,
    from_associated_sites,
    from_recorded,
    from_recorded_by,
    from_updated,
    from_updated_by,
    from_visited,
    from_visited_by,
    from_record_quality,
    'malcolm',
    site_id
FROM work.nzaa_sitereview;
SELECT setval('nzaa_sitereview_id_seq',
    (SELECT id FROM nzaa_sitereview ORDER BY id DESC LIMIT 1) + 1);


