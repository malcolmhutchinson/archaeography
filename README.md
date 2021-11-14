archaeography.nz
----------------

Experiments with archaeological data.

PLEASE NOTE: This project is now abandoned. 

I no longer have any involvement in archaeology, and I am not a 
member of the New Zealand Archaelogical Association.

The archaeography project was an experimental model of the [NZ
Archaeological Association's](http://nzarchaeology.org) (NZAA) Site
Recording Scheme (SRS). The project was active from 2012 until 2016, 
and was abandoned sometime in 2017. This comment was added 
2021-11-14.

---

It is an engineering prototype, the purpose of
which is to provide understanding of the problems involved with
handling large volumes of information describing archaeological sites.

The Python code here expresses, in a Django web framework, some of the
functions of an information system for handling the records in the SRS.

NOTE: There are NO DATA BELONGING TO THE NZAA present in this
codebase. 


Mission
---------

This is a machine for handling archaeological site records. The
intention is to provide a normalised relational database describing
the NZAA Site Recording Scheme. This database includes a web
interface, and provides a variety of functions for searching, sorting
and viewing copies of the archaeological site records held in the SRS.

The problem being studied is how to extract the maximum value in
knowledge from those records. It's about easy ways to find and view
archaeological site records, ways of sorting and selecting them, and
developing techniques for analysing them.

The immediate purpose is to to provide a machine for interacting with
the records in the SRS, which permits the interrogation of the
database as a whole. I wanted an easy way to view individual site
records, to search the collection, and to compile lists of site
records.

The project is a model of the SRS. It includes methods for preparing
new site records, or updates to existing site records, for submission
to the filekeeper. It is also intended to model processes by which a
filekeeper may manage submitted records, assess them and accession them
into the formal collection.

This project is experimental. It's overall purpose is to gain a
greater understanding of the national archaeological dataset, by
applying relational database techniques to it.


Functions
---------

The code in this repository provides a website constructed in the
Django framework. The website can be used to interact with a copy of
the dataset drawn from the SRS.

The archaeography code provides a set of basic functions which can be
performed on archaeological records.


1.  Viewing the archaeological site record collection. This includes:

    -   the ability to select subsets of the site record collection by
        geographic groupings such as region, territorial authority,
        NZAA recording region, or map sheet;

    -   the ability to select records according to archaeological site
        type, period, ethnicity, or features recorded within;

    -   viewing any individual site record in an efficient and intuative
        way, showing all associated documents, photos and files
        collected with it.

1.  Compiling, editing and managing site update records.

    Providing mechanisims by which new site records, and site update
    records, can be compiled online. This implies a process, from
    creation and subsequent editing of a record, to it's submission to
    a filekeeper for assessment, and it's accession into the formal
    collection. 

    This process is served by functions to sort and organise site
    update records, providing a means to control large numbers of
    records in a production-line. These functions are:

    -   a place to record archaeological data associated with an
        existing site record, or a previously unrecorded one;

    -   the ability to edit such records at the author's discretion;

    -   a means by which many site update records may be staged, or sorted by
        urgency; and

    -   a means by which a filekeeper can assess the record, change it
        as necessary, and then either accept it, or send it back to the
        author with a query attached.

1.  Providing a test-bed for developing analytical techniques.

    This is necessarily the least specific function of the project. I
    aim to develop a normalised relational database structure on which
    any number of applications can be built. 


More information
----------------

The technical descriptions of the database, the data dictionary and
other such documents are all included in the site manuals. These are
available at `/manuals/` from the project server.


Installing archaeography
------------------------

Detailed, step-by-step instructions for installing the archaeography
project code into a Django development environment are included in the
[INSTALL](https://github.com/malcolmhutchinson/archaeography/blob/master/INSTALL.md)
document.
