Recent changes
==============

<p class='note'><a href='/nzaa/changes/'>/nzaa/changes</a></p>

The list of records which have changed, since the last time any record
was [scraped](/manuals/nzaa/scraping_archsite).



### How this works

The archaeography server scans [ArchSite](http://archsite.org.nz)
every week, going systematically through the dataset, checking all the
site records. This is done in the middle of the night, to minimise the
load on the ArchSite servers.

Each time a site record is scaped, a timestamp is written. This is
displayed on the record in the
[last checked against ArchSite](/manuals/nzaa/last_checked)
field. This timestamp is written regardless of whether the record has
changed or not.

The incoming data are compared against what is already in the local
database. If any differences are observed, the local record is
updated, and a timestamp is written into the
[last known change](/manuals/nzaa/last_known_change) field.

If a record has a
[last known change](/manuals/nzaa/last_known_change) date the same as the
[last checked](/manuals/nzaa/last_checked), then we know that it
changed, during that last scan.

Note that if the same record is scanned again a day or two afterwards, it
will likely fail this test, and not appear on the "recent changes"
list.

See also [last checked](/manuals/nzaa/last_checked).  
See also [last known change](/manuals/nzaa/last_known_change).
