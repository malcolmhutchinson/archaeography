Normalising site records
========================

When the SRS was organised as a paper scheme, a site record was
composed of the original record, and then zero or more update
records. It was possible to trace the history of the site record by
arranging the pages found in it by date.

Modelling this history in the project database has advantages. We can
determine the quality of a record in part from the number of times it
has been updated. We can identify records that have very little
information in them, so these records can be targeted for updates. We
can ask the computer to tell us how much information is associated
with each site record. And we can use these data on the aggregate
scale of thousands of records to understand something of the nature
and quality of the information in the whole scheme.

The data downloaded from ArchSite do not reflect this structure. The
process of correcting them, so they do, is called _normalising_ the
site record.

Normalisation is a process, which requires that a human read the
record (including the scanned copies of the original paper pages), and
identify:

1.  the original record, the name of the person making it, the date
    the record was created, and any 
    [aggregate data](/manuals/nzaa/site_record_fields) in fields like
    `features` which may not have already been captured,

1.  any subsequent update records, capturing the same data about who
    and when, as for the initial site recording.

Following the identification:

1.  `Update` objects are created in the database for the first record
    and subsequent updates, and associated with the site record.

1.  The files downloaded from ArchSite are identified and associated
    with the `Update` objects.

The result is a site record with several Update records:

    Update 0    - always the ArchSite copy
    Update 1    - The original record.
    Update n    - Subsequent updates identified by date and actor.

You can now view the record as a series of update events, which should
provide a history of the site record. We can also provide aggregate
counts of the number of pages associated with each record.

Structuring the data included with an archaeological site record in
this way will help to analyse the quality and accuracy of the
information in the SRS.



