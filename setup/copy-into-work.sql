-- copy-into-work.sql

--  Create copies of the relevant tables into schema work.  Relevant
--  tables contain proprietary data (ie. not LINZ or StatsNZ
--  data). This is intended to capture all proprietary data into the
--  schema work, and from there to be dumped to SQL file.

--  The resulting file can be used to move these data between
--  installations... they go into the work schema, not the public one,
--  so they won't interfere with a working installation.


-- The users and groups.
DROP TABLE IF EXISTS work.auth_group;
DROP TABLE IF EXISTS work.auth_group_permissions;
DROP TABLE IF EXISTS work.auth_permission;
DROP TABLE IF EXISTS work.auth_user;
DROP TABLE IF EXISTS work.auth_user_groups;
DROP TABLE IF EXISTS work.auth_user_user_permissions;

CREATE TABLE work.auth_group AS SELECT * FROM auth_group;
CREATE TABLE work.auth_group_permissions
    AS SELECT * FROM auth_group_permissions;
CREATE TABLE work.auth_permission AS SELECT * FROM auth_permission;
CREATE TABLE work.auth_user AS SELECT * FROM auth_user;
CREATE TABLE work.auth_user_groups AS SELECT * FROM auth_user_groups;
CREATE TABLE work.auth_user_user_permissions
    AS SELECT * FROM auth_user_user_permissions;

-- Aerial photos, georeferencing information etc.
DROP TABLE IF EXISTS work.geolib_aerialfile;
DROP TABLE IF EXISTS work.geolib_aerialframe;
DROP TABLE IF EXISTS work.geolib_aerialrun;
DROP TABLE IF EXISTS work.geolib_aerialsurvey;
DROP TABLE IF EXISTS work.geolib_waterways;

CREATE TABLE work.geolib_aerialfile AS SELECT * FROM geolib_aerialfile;
CREATE TABLE work.geolib_aerialframe AS SELECT * FROM geolib_aerialframe;
CREATE TABLE work.geolib_aerialrun AS SELECT * FROM geolib_aerialrun;
CREATE TABLE work.geolib_aerialsurvey AS SELECT * FROM geolib_aerialsurvey;
CREATE TABLE work.geolib_waterways AS SELECT * FROM geolib_waterways;

--  Members, contacts and organisations.
DROP TABLE IF EXISTS work.members_address;
DROP TABLE IF EXISTS work.members_organisation;
DROP TABLE IF EXISTS work.members_person;
DROP TABLE IF EXISTS work.members_member;

CREATE TABLE work.members_address AS SELECT * FROM members_address;
CREATE TABLE work.members_organisation AS SELECT * FROM members_organisation;
CREATE TABLE work.members_person AS SELECT * FROM members_person;
CREATE TABLE work.members_member AS SELECT * FROM members_member;

-- Authoratative records currently reside on okaraina.
DROP TABLE IF EXISTS work.nzaa_actor;
DROP TABLE IF EXISTS work.nzaa_actor_sites;
DROP TABLE IF EXISTS work.nzaa_feature;
DROP TABLE IF EXISTS work.nzaa_feature_sites;
DROP TABLE IF EXISTS work.nzaa_newsite;
DROP TABLE IF EXISTS work.nzaa_periods;
DROP TABLE IF EXISTS work.nzaa_periods_sites;
DROP TABLE IF EXISTS work.nzaa_site;
DROP TABLE IF EXISTS work.nzaa_sitelist;
DROP TABLE IF EXISTS work.nzaa_sitelist_sites;
DROP TABLE IF EXISTS work.nzaa_sitereview;
DROP TABLE IF EXISTS work.nzaa_update;

CREATE TABLE work.nzaa_actor AS SELECT * FROM nzaa_actor;
CREATE TABLE work.nzaa_actor_sites AS SELECT * FROM nzaa_actor_sites;
CREATE TABLE work.nzaa_feature AS SELECT * FROM nzaa_feature;
CREATE TABLE work.nzaa_feature_sites AS SELECT * FROM nzaa_feature_sites;
CREATE TABLE work.nzaa_newsite AS SELECT * FROM nzaa_newsite;
CREATE TABLE work.nzaa_periods AS SELECT * FROM nzaa_periods;
CREATE TABLE work.nzaa_periods_sites AS SELECT * FROM nzaa_periods_sites;
CREATE TABLE work.nzaa_site AS SELECT * FROM nzaa_site;
CREATE TABLE work.nzaa_sitelist AS SELECT * FROM nzaa_sitelist;
CREATE TABLE work.nzaa_sitelist_sites AS SELECT * FROM nzaa_sitelist_sites;
CREATE TABLE work.nzaa_sitereview AS SELECT * FROM nzaa_sitereview;
CREATE TABLE work.nzaa_update AS SELECT * FROM nzaa_update;
