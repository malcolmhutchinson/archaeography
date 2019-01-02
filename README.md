archaeography.nz
----------------

Experiments with archaeological data.

This is the boundary report branch. For a detailed background to the
archaeography project, checkout the master branch.


The breport branch
------------------

The boundary report branch. Development on functions to provide lists
of archaeological sites intersecting with and adjacent to arbitrary
polygon geometries.

The user can upload a polygon geometry, as a KML file. This is
injected into a database table, where the model can be used to extract
lists of site records by distance -- those inside the shape, those
intersecting, and those adjacent. It will also collect cadastral
parcels intersecting with the shape.



More information
----------------

The technical descriptions of the database, the data dictionary and
other such documents are all included in the site manuals. These are
available at `/manuals/` from the project server.


Installing archaeography
------------------------

Detailed, step-by-step instructions for installing the archaeography
project code into a Django development environment are included in the
(INSTALL)[https://github.com/malcolmhutchinson/archaeography/blob/master/INSTALL.md]
document.
