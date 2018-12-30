Introduction to archaeography.nz
================================


The archaeography project is an experiment in archaeological records
research. At it's heart is a model of the
[NZ Archaeological Association's](/manuals/nzaa/nzaa/)
[Site Recording Scheme (SRS)](/manuals/nzaa/site_recording_scheme/).

I started this project, because I wanted to see what insights into the
national archaeological dataset could be gained by applying modern
relational database design and engineering ideas.

This website contains a model of the SRS. I have downloaded copies of
the archaeological records from ArchSite, and injected them into a
spatially-enabled relational database. I've then used the Python
programming language and the Django web framework to build an
interface to the archaeological records.

I want to be able to do computational research on the national
archaeological dataset. I want to see what we can learn about the
presence of humans in New Zealand by combing through the
seventy-thousand-odd archaeologcial site records collected by the
NZAA, by selecting and comparing them, by stacking them in different
ways and seeing what patterns emerge. I want to understand the nature
of the information in the SRS, how much of it there is, and how
accurate it is.

This website represents my efforts to do that. Archaeography.nz is an
experiment in understanding what is involved in building and using an
archaeological data machine. By doing this, I expect to come to know
more about the national archaeological dataset. I also hope to learn
something about how to build software to extract the maximum available
knowledge from it.

The history of the SRS as a paper-based scheme has a critical
influence on the architecture of the project.  The archaeography
machine is desgned to represent all the data in the scheme; the
archaeological data in formats accessible to computation, and the
change history of site records.

There are four main research components to the project.

1.  Understanding the national archaeological dataset,

2.  [developing methods for] managing the quality of the archaeological
    data,

3.  extracting knowledge from the dataset, and

4.  [developing methods for] expanding the dataset.



Understanding the national archaeological dataset
-------------------------------------------------

The first part of the problem is understanding the nature of the
problem. Much study went into analysing the composition of
archaeological site records, as we find them on the Association's
website ArchSite. 

Processing the incoming site record data, causing them to conform to
normalised database structures, is the first operation. Much of the
dataset is encoded as scans of paper records, and as such is beyond
the reach of conventional computational methods.

A very labour-intensive operation is required to recover data encoded
in those scans. Someone has to read the records and type in things
like lists of archaeologcal features, or the name of the person making
the record.

The interface can help this process a lot. The project provides
software to help with the task of
[normalising site and update records](/manuals/nzaa/normalise). 

We should also be able to quantify the data in the SRS. It is
relatively easy to know how many archaeological sites are
recorded. But how much information is encoded for each site? How many
of the records are sparse, providing little more than a location? How
many contain comprehensive archaeolgical data?



Managing the quality of archaeologcal data
--------------------------------------------

This component is about what means can be used to determine the
quality and accuracy of data in the collection, and what techniques
and procedures can be applied to ensure an increasing quality over
time.

Controlling quality starts with information being submitted by
archaeologists, to the filekeepers, for consideration for inclusion in
the SRS. 

A site record goes through a process, from its creation, through
cycles of editing before being submitted to a filekeeper for
consideration.  When the filekeeper is satisfied with the quality of
the record, they may formally accession the changes into the
collection.

The archaeologist requires a place where they may assemble their site
records from field notes and other data. It is not uncommon for a
researcher to have several dozens of new sites to record, and some
means of managing a production line of records would be helpful.

The filekeeper needs to be informed of submitted records, and they
need tools to rapidly assess the quality of submissions, and accession
acceptable records.

Bear in mind the national scope of the SRS. On any day, multiple site
update records may be filed by archaeologists around the country. The
system must be able to help the filekeeper deal with volumes of
incoming records.

The archaeography project attempts to model a process which provides
the users and the filekeepers with tools for managing large numbers of
site update records in various stages of production. The toolset
includes consideration for asessing the quality of the incoming
information, and a means of separating new records, which have not yet
been assessed by a filekeeper, from the authoratative collection.

The history of a record is critical to understanding the quality of
the information in it. It should be possible to identify a complete
change history for any site record, and to undo any changes made by
any user or filekeeper. To answer this requirement, the project
captures changes to a site record in a change ticket, preserving the
old values and providing a method for reversing undesirable
modifications.


Extracting knowledge from the dataset
-------------------------------------

The project provides a simple web-based interface to lists of site
records, and to individual records. Basic methods for searching site
records on a variety of archaeological and geographic criteria are
included.

The archaeologist wants to be able to find relevant site records
quickly, and to read them easily. They want to list sets of relevant
sites, and to compare them on a variety of archaeological and
geographic data.

The first part of getting the knowledge out of the data is providing
an intuative interface. So when you look at a site record, you see all
the archaeological data, including the scans of the paper files, and
useful geographic locators all in one place.  You should be able to
click quickly through any list of records, and come back to your list
at any time. Records should be linked by natural groupings: it should
be easy to get a list of all the historic archaeological sites in
Otago, or all the pa sites in Hamilton.

The basic interface includes useful location data, like the closest
road or named place to the archaeological site. Individual site
records are expected to be easy to read, with priority given the
relevant archaeological data.

Certain analytical tools can be provided. The simplest is a
list-handling function, which enables an archaeologist to compile
lists of site records on arbitrary criteria, and then examine those
records individually. Some basic set algebra can applied to lists,
like the union and intersection functions.

The project is also intended to be a test bed for experimental
computational techniques. 




Expanding the dataset
---------------------

We are investigating methods for including geographic data with
archaeological site records.

The idea behind this is that we should be able to record all types of
data describing archaeological evidence for any archaeological
site. This includes spatial data; the points, lines and polygons which
archaeologists collect with their GPS handsets and survey equipment.

So a component of the archaeography machine is set aside to experiment
with ways of organising spatial data alongside the photos and
descriptions, and of associating these clearly with individual update
records, so we can tell where all of our archaeological information
comes from.

We also want to be demonstrating this capability by creating site
update records which include spatial data derived from analysis of
remote sensing data; lidar and orthophotography offered by Land
Information New Zealand (LINZ). 



