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